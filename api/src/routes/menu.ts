import { Router } from "express";
import { prisma } from "../lib/prisma.js";

export const menuRouter = Router();

const today = () => new Date().toISOString().slice(0, 10);

menuRouter.get("/api/menu/today", async (req, res) => {
  const date = req.query.date ? String(req.query.date).slice(0, 10) : today();

  const menuDay = await prisma.menuDay.findUnique({
    where: { date },
    include: { menuItems: true },
  });

  if (!menuDay) {
    return res.json({
      date,
      scrapedAt: null,
      items: [],
      message: "No menu for this date. Run POST /api/scrape/run to fetch.",
    });
  }

  return res.json({
    date: menuDay.date,
    sourceUrl: menuDay.sourceUrl,
    scrapedAt: menuDay.scrapedAt.toISOString(),
    items: menuDay.menuItems.map((it) => ({
      id: it.id,
      name: it.name,
      mealPeriod: it.mealPeriod,
      calories: it.calories,
      protein: it.protein,
      carbs: it.carbs,
      fat: it.fat,
      tags: it.tags,
    })),
  });
});
