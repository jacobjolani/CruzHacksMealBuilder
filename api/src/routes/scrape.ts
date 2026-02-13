import { Router } from "express";
import { prisma } from "../lib/prisma.js";
import { scrapeBerkeleyMenu } from "../services/scraper.js";

export const scrapeRouter = Router();

const today = () => new Date().toISOString().slice(0, 10);

scrapeRouter.post("/api/scrape/run", async (req, res) => {
  const date = today();
  try {
    const items = await scrapeBerkeleyMenu();

    const menuDay = await prisma.menuDay.upsert({
      where: { date },
      create: {
        date,
        sourceUrl: process.env.BERKELEY_MENU_URL ?? undefined,
        menuItems: {
          create: items.map((it) => ({
            name: it.name,
            mealPeriod: it.mealPeriod,
            calories: it.calories,
            protein: it.protein,
            carbs: it.carbs,
            fat: it.fat,
            tags: it.tags ?? null,
          })),
        },
      },
      update: {
        scrapedAt: new Date(),
        sourceUrl: process.env.BERKELEY_MENU_URL ?? undefined,
        menuItems: {
          deleteMany: {},
          create: items.map((it) => ({
            name: it.name,
            mealPeriod: it.mealPeriod,
            calories: it.calories,
            protein: it.protein,
            carbs: it.carbs,
            fat: it.fat,
            tags: it.tags ?? null,
          })),
        },
      },
      include: { menuItems: true },
    });

    return res.json({
      ok: true,
      date,
      itemCount: menuDay.menuItems.length,
    });
  } catch (e) {
    console.error("Scrape error:", e);
    return res.status(500).json({ error: "Scrape failed", message: String(e) });
  }
});
