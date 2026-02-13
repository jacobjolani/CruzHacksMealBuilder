import { Router } from "express";
import { prisma } from "../lib/prisma.js";
import { buildPlan, type MacroTargets, type MenuItemRow } from "../services/planner.js";
import { getCachedPlan, setCachedPlan, invalidatePlan, targetsSignature } from "../services/cache.js";

export const planRouter = Router();

const today = () => new Date().toISOString().slice(0, 10);

function getSessionId(req: unknown): string {
  const r = req as { sessionId?: string; cookies?: { sessionId?: string } };
  return r.sessionId ?? r.cookies?.sessionId ?? "";
}

async function resolveTargets(
  reqBody: Record<string, unknown> | undefined,
  sessionId: string
): Promise<MacroTargets> {
  const fromBody: MacroTargets = {
    calories: reqBody?.dailyCalories != null ? Number(reqBody.dailyCalories) : undefined,
    protein: reqBody?.dailyProtein != null ? Number(reqBody.dailyProtein) : undefined,
    carbs: reqBody?.dailyCarbs != null ? Number(reqBody.dailyCarbs) : undefined,
    fat: reqBody?.dailyFat != null ? Number(reqBody.dailyFat) : undefined,
  };
  const hasBody = [fromBody.calories, fromBody.protein, fromBody.carbs, fromBody.fat].some(
    (v) => v != null && Number.isFinite(v) && v > 0
  );
  if (hasBody) return fromBody;

  const profile = await prisma.userProfile.findUnique({
    where: { sessionId },
  });
  if (!profile)
    return fromBody;
  return {
    calories: profile.dailyCalories ?? undefined,
    protein: profile.dailyProtein ?? undefined,
    carbs: profile.dailyCarbs ?? undefined,
    fat: profile.dailyFat ?? undefined,
  };
}

planRouter.post("/api/plan/generate", async (req, res) => {
  const sessionId = getSessionId(req);
  const date = (req.body?.date as string)?.slice(0, 10) ?? today();

  const targets = await resolveTargets(req.body, sessionId);
  const targetsSig = targetsSignature(targets);

  if (sessionId) {
    const cached = getCachedPlan(date, sessionId, targetsSig);
    if (cached) return res.json(cached);
  }

  const menuDay = await prisma.menuDay.findUnique({
    where: { date },
    include: { menuItems: true },
  });

  if (!menuDay || menuDay.menuItems.length === 0) {
    return res.status(404).json({
      error: "No menu for this date",
      message: "Run POST /api/scrape/run first to fetch the menu.",
    });
  }

  const items: MenuItemRow[] = menuDay.menuItems.map((it) => ({
    id: it.id,
    name: it.name,
    mealPeriod: it.mealPeriod,
    calories: it.calories,
    protein: it.protein,
    carbs: it.carbs,
    fat: it.fat,
    tags: it.tags,
  }));

  if (process.env.NODE_ENV !== "production") {
    console.log("[plan/generate] targets:", targets, "menuItems:", items.length);
  }

  const result = buildPlan(items, targets);

  const mealsJson = JSON.stringify({
    breakfast: result.breakfast.items,
    lunch: result.lunch.items,
    dinner: result.dinner.items,
  });

  if (sessionId) {
    await prisma.mealPlan.create({
      data: {
        menuDayId: menuDay.id,
        sessionId,
        totalsCalories: result.totals.calories,
        totalsProtein: result.totals.protein,
        totalsCarbs: result.totals.carbs,
        totalsFat: result.totals.fat,
        meals: mealsJson,
      },
    });
    setCachedPlan(date, sessionId, targetsSig, { date, ...result });
  }

  return res.json({ date, ...result });
});

planRouter.post("/api/plan/regenerate", async (req, res) => {
  const sessionId = getSessionId(req);
  const meal = (req.query.meal as string)?.toLowerCase();
  if (!["breakfast", "lunch", "dinner"].includes(meal)) {
    return res.status(400).json({ error: "Invalid meal; use breakfast, lunch, or dinner" });
  }

  const date = (req.body?.date as string)?.slice(0, 10) ?? today();
  invalidatePlan(date, sessionId);

  const targets = await resolveTargets(req.body, sessionId);

  const menuDay = await prisma.menuDay.findUnique({
    where: { date },
    include: { menuItems: true },
  });

  if (!menuDay || menuDay.menuItems.length === 0) {
    return res.status(404).json({ error: "No menu for this date" });
  }

  const items: MenuItemRow[] = menuDay.menuItems.map((it) => ({
    id: it.id,
    name: it.name,
    mealPeriod: it.mealPeriod,
    calories: it.calories,
    protein: it.protein,
    carbs: it.carbs,
    fat: it.fat,
    tags: it.tags,
  }));

  if (process.env.NODE_ENV !== "production") {
    console.log("[plan/regenerate] meal:", meal, "targets:", targets, "menuItems:", items.length);
  }

  const result = buildPlan(items, targets);
  const mealsJson = JSON.stringify({
    breakfast: result.breakfast.items,
    lunch: result.lunch.items,
    dinner: result.dinner.items,
  });

  const targetsSig = targetsSignature(targets);
  if (sessionId) {
    await prisma.mealPlan.create({
      data: {
        menuDayId: menuDay.id,
        sessionId,
        totalsCalories: result.totals.calories,
        totalsProtein: result.totals.protein,
        totalsCarbs: result.totals.carbs,
        totalsFat: result.totals.fat,
        meals: mealsJson,
      },
    });
    setCachedPlan(date, sessionId, targetsSig, { date, ...result });
  }

  return res.json({ date, ...result });
});

function sumItems(arr: { calories: number; protein: number; carbs: number; fat: number }[]) {
  return arr.reduce(
    (a, i) => ({
      calories: a.calories + i.calories,
      protein: a.protein + i.protein,
      carbs: a.carbs + i.carbs,
      fat: a.fat + i.fat,
    }),
    { calories: 0, protein: 0, carbs: 0, fat: 0 }
  );
}

planRouter.post("/api/plan/swap", async (req, res) => {
  const { meal, outItemId, inItemId, date: bodyDate } = req.body ?? {};
  const sessionId = getSessionId(req);
  const date = bodyDate ? String(bodyDate).slice(0, 10) : today();

  if (!meal || !outItemId || !inItemId) {
    return res.status(400).json({ error: "meal, outItemId, and inItemId required" });
  }
  const mealKey = String(meal).toLowerCase() as "breakfast" | "lunch" | "dinner";
  if (!["breakfast", "lunch", "dinner"].includes(mealKey)) {
    return res.status(400).json({ error: "Invalid meal" });
  }

  const menuDay = await prisma.menuDay.findUnique({
    where: { date },
    include: { menuItems: true },
  });
  if (!menuDay) return res.status(404).json({ error: "No menu for this date" });

  const outItem = menuDay.menuItems.find((i) => i.id === outItemId);
  const inItem = menuDay.menuItems.find((i) => i.id === inItemId);
  if (!outItem || !inItem) {
    return res.status(400).json({ error: "Item not found" });
  }

  invalidatePlan(date, sessionId);

  const latest = await prisma.mealPlan.findFirst({
    where: { sessionId, menuDayId: menuDay.id },
    orderBy: { createdAt: "desc" },
  });

  if (!latest) {
    return res.status(404).json({ error: "No plan to swap; generate a plan first" });
  }

  const meals = JSON.parse(latest.meals) as {
    breakfast: (typeof menuDay.menuItems)[];
    lunch: (typeof menuDay.menuItems)[];
    dinner: (typeof menuDay.menuItems)[];
  };
  const slot = meals[mealKey];
  if (!slot) return res.status(400).json({ error: "Invalid meal slot" });

  const idx = slot.findIndex((i: { id: string }) => i.id === outItemId);
  if (idx === -1) return res.status(400).json({ error: "Item not in this meal" });

  const newSlot = [...slot];
  newSlot[idx] = inItem;
  meals[mealKey] = newSlot;

  const allItems = [...meals.breakfast, ...meals.lunch, ...meals.dinner];
  const totals = sumItems(allItems);

  await prisma.mealPlan.create({
    data: {
      menuDayId: menuDay.id,
      sessionId,
      totalsCalories: totals.calories,
      totalsProtein: totals.protein,
      totalsCarbs: totals.carbs,
      totalsFat: totals.fat,
      meals: JSON.stringify(meals),
    },
  });

  const breakfast = { items: meals.breakfast, ...sumItems(meals.breakfast) };
  const lunch = { items: meals.lunch, ...sumItems(meals.lunch) };
  const dinner = { items: meals.dinner, ...sumItems(meals.dinner) };
  const deltas = { calories: 0, protein: 0, carbs: 0, fat: 0 };

  const targetsSig = targetsSignature({});
  setCachedPlan(date, sessionId, targetsSig, { date, breakfast, lunch, dinner, totals, deltas });

  return res.json({ date, breakfast, lunch, dinner, totals, deltas });
});
