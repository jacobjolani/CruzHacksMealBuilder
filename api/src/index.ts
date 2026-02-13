import express from "express";
import cookieParser from "cookie-parser";
import cors from "cors";
import { sessionMiddleware } from "./middleware/session.js";
import { profileRouter } from "./routes/profile.js";
import { scrapeRouter } from "./routes/scrape.js";
import { menuRouter } from "./routes/menu.js";
import { planRouter } from "./routes/plan.js";
import cron from "node-cron";
import { scrapeBerkeleyMenu } from "./services/scraper.js";
import { prisma } from "./lib/prisma.js";

const app = express();
const PORT = Number(process.env.PORT) || 4000;

app.use(cors({ origin: true, credentials: true }));
app.use(cookieParser());
app.use(express.json());
app.use(sessionMiddleware);

app.use(profileRouter);
app.use(scrapeRouter);
app.use(menuRouter);
app.use(planRouter);

app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", ts: new Date().toISOString() });
});

// Daily scrape at 5 AM
cron.schedule("0 5 * * *", async () => {
  const date = new Date().toISOString().slice(0, 10);
  try {
    const items = await scrapeBerkeleyMenu();
    await prisma.menuDay.upsert({
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
    });
    console.log(`[cron] Scraped ${items.length} items for ${date}`);
  } catch (e) {
    console.error("[cron] Scrape failed:", e);
  }
});

app.listen(PORT, () => {
  console.log(`API http://localhost:${PORT}`);
});
