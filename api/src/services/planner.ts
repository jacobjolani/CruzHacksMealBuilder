/**
 * Deterministic meal planner: build 3 meals (breakfast, lunch, dinner) to hit macro targets.
 * Priority: protein first, then carbs, then fat, then calories. Stops when adding an item would increase error.
 */

export type MacroTargets = {
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
};

export type MenuItemRow = {
  id: string;
  name: string;
  mealPeriod: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  tags?: string | null;
};

export type MealSlot = "breakfast" | "lunch" | "dinner";

export type PlanMeal = { items: MenuItemRow[]; calories: number; protein: number; carbs: number; fat: number };

export type PlanResult = {
  breakfast: PlanMeal;
  lunch: PlanMeal;
  dinner: PlanMeal;
  totals: { calories: number; protein: number; carbs: number; fat: number };
  deltas: { calories: number; protein: number; carbs: number; fat: number };
};

const WEIGHTS = { protein: 4, carbs: 2, fat: 1, calories: 0.5 };
const TOLERANCE = 0.05;
const MAX_ITEMS_PER_MEAL = 5;

function slotError(
  current: { calories: number; protein: number; carbs: number; fat: number },
  slotTargets: MacroTargets
): number {
  let err = 0;
  const cur = current as Record<string, number>;
  for (const [k, target] of Object.entries(slotTargets)) {
    if (target == null || target <= 0) continue;
    const c = cur[k] ?? 0;
    const diff = c - target;
    const norm = Math.max(target, 1);
    const overshoot = diff > 0 ? (["calories", "fat", "carbs"].includes(k) ? 1.5 : 1) : 1;
    const normErr = (diff > 0 ? overshoot * (diff / norm) : Math.abs(diff) / norm) * (WEIGHTS[k as keyof typeof WEIGHTS] ?? 1);
    err += normErr;
  }
  return err;
}

/** Fisher–Yates shuffle; mutates array */
function shuffle<T>(arr: T[]): T[] {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function fillSlot(
  items: MenuItemRow[],
  slotTargets: MacroTargets,
  usedIds: Set<string>,
  maxItems: number
): MenuItemRow[] {
  const chosen: MenuItemRow[] = [];
  let current = { calories: 0, protein: 0, carbs: 0, fat: 0 };

  for (let i = 0; i < maxItems; i++) {
    const currentErr = slotError(current, slotTargets);
    if (currentErr <= TOLERANCE) break;

    let bestCandidates: MenuItemRow[] = [];
    let bestErr = Infinity;

    for (const it of items) {
      if (usedIds.has(it.id)) continue;
      const trial = {
        calories: current.calories + it.calories,
        protein: current.protein + it.protein,
        carbs: current.carbs + it.carbs,
        fat: current.fat + it.fat,
      };
      const err = slotError(trial, slotTargets);
      if (err < bestErr) {
        bestErr = err;
        bestCandidates = [it];
      } else if (err === bestErr) {
        bestCandidates.push(it);
      }
    }

    if (bestCandidates.length === 0 || bestErr >= currentErr) break;
    const best = bestCandidates[Math.floor(Math.random() * bestCandidates.length)];
    chosen.push(best);
    usedIds.add(best.id);
    current = {
      calories: current.calories + best.calories,
      protein: current.protein + best.protein,
      carbs: current.carbs + best.carbs,
      fat: current.fat + best.fat,
    };
  }

  return chosen;
}

function sumItems(items: MenuItemRow[]): { calories: number; protein: number; carbs: number; fat: number } {
  return items.reduce(
    (acc, it) => ({
      calories: acc.calories + it.calories,
      protein: acc.protein + it.protein,
      carbs: acc.carbs + it.carbs,
      fat: acc.fat + it.fat,
    }),
    { calories: 0, protein: 0, carbs: 0, fat: 0 }
  );
}

/**
 * Build three meals from menu items. Partitions by mealPeriod when possible; otherwise uses all items.
 * Shuffles pools so each call can produce different meals; greedy + random tie-break for variety.
 */
export function buildPlan(
  items: MenuItemRow[],
  targets: MacroTargets
): PlanResult {
  const slotTargets: MacroTargets = {};
  if (targets.calories != null && targets.calories > 0) slotTargets.calories = targets.calories / 3;
  if (targets.protein != null && targets.protein > 0) slotTargets.protein = targets.protein / 3;
  if (targets.carbs != null && targets.carbs > 0) slotTargets.carbs = targets.carbs / 3;
  if (targets.fat != null && targets.fat > 0) slotTargets.fat = targets.fat / 3;

  if (Object.keys(slotTargets).length === 0) {
    slotTargets.calories = 2000 / 3;
    slotTargets.protein = 50;
    slotTargets.carbs = 60;
    slotTargets.fat = 22;
  }

  const breakfastPool = items.filter((i) => i.mealPeriod === "breakfast" || i.mealPeriod === "any");
  const lunchPool = items.filter((i) => i.mealPeriod === "lunch" || i.mealPeriod === "any");
  const dinnerPool = items.filter((i) => i.mealPeriod === "dinner" || i.mealPeriod === "any");

  const fallback = items.length > 0 ? items : [];
  const brunch = shuffle(breakfastPool.length > 0 ? [...breakfastPool] : [...fallback]);
  const lunchItems = shuffle(lunchPool.length > 0 ? [...lunchPool] : [...fallback]);
  const dinnerItems = shuffle(dinnerPool.length > 0 ? [...dinnerPool] : [...fallback]);

  const usedIds = new Set<string>();

  const breakfastItems = fillSlot(brunch, slotTargets, usedIds, MAX_ITEMS_PER_MEAL);
  const lunchItemsList = fillSlot(lunchItems, slotTargets, usedIds, MAX_ITEMS_PER_MEAL);
  const dinnerItemsList = fillSlot(dinnerItems, slotTargets, usedIds, MAX_ITEMS_PER_MEAL);

  const breakfast = { items: breakfastItems, ...sumItems(breakfastItems) };
  const lunch = { items: lunchItemsList, ...sumItems(lunchItemsList) };
  const dinner = { items: dinnerItemsList, ...sumItems(dinnerItemsList) };

  const totals = {
    calories: breakfast.calories + lunch.calories + dinner.calories,
    protein: breakfast.protein + lunch.protein + dinner.protein,
    carbs: breakfast.carbs + lunch.carbs + dinner.carbs,
    fat: breakfast.fat + lunch.fat + dinner.fat,
  };

  const deltas = {
    calories: (targets.calories ?? 0) - totals.calories,
    protein: (targets.protein ?? 0) - totals.protein,
    carbs: (targets.carbs ?? 0) - totals.carbs,
    fat: (targets.fat ?? 0) - totals.fat,
  };

  return { breakfast, lunch, dinner, totals, deltas };
}
