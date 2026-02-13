/**
 * Berkeley dining menu scraper. Isolated adapter: if the site changes markup, update selectors here only.
 * Uses Playwright for JS-rendered content. Returns items with mealPeriod inferred or "any".
 */

const BERKELEY_MENU_URL = process.env.BERKELEY_MENU_URL ?? "https://dining.berkeley.edu/menus/";

export type ScrapedItem = {
  name: string;
  mealPeriod: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  tags?: string | null;
};

function parseNum(s: string | null | undefined): number {
  if (s == null || s === "") return 0;
  const cleaned = String(s).replace(/,/g, "").replace(/g$/i, "").trim();
  const n = parseFloat(cleaned);
  return Number.isFinite(n) ? Math.max(0, n) : 0;
}

export async function scrapeBerkeleyMenu(): Promise<ScrapedItem[]> {
  const { chromium } = await import("playwright");
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    await page.goto(BERKELEY_MENU_URL, { waitUntil: "networkidle", timeout: 30000 });
  } catch (e) {
    await browser.close();
    throw new Error(`Failed to load menu page: ${e}`);
  }

  const items: ScrapedItem[] = [];

  try {
    // Berkeley uses .recip for menu items; click opens popup with nutrition
    const recipSelectors = await page.$$(".recip");
    for (let i = 0; i < recipSelectors.length; i++) {
      const el = recipSelectors[i];
      const name = (await el.textContent())?.trim() ?? "";
      if (!name) continue;

      await el.scrollIntoViewIfNeeded();
      await el.click();
      await page.waitForSelector(".cald-popup-wrapper.show", { timeout: 5000 }).catch(() => null);

      let calories = 0,
        protein = 0,
        carbs = 0,
        fat = 0;
      const details = await page.$(".recipe-details-wrap");
      if (details) {
        const lis = await details.$$("li");
        for (const li of lis) {
          const text = (await li.textContent())?.toLowerCase() ?? "";
          const raw = (await li.textContent())?.trim() ?? "";
          const val = raw.split(":")[1]?.trim();
          if (text.includes("calories") && !text.includes("from")) calories = parseNum(val);
          else if (text.includes("total") && text.includes("fat")) fat = parseNum(val);
          else if (text.includes("carbohydrate") || text.includes("carbs")) carbs = parseNum(val);
          else if (text.includes("protein")) protein = parseNum(val);
        }
      }

      const closeBtn = await page.$("a.cald-close");
      if (closeBtn) await closeBtn.click();
      await page.waitForTimeout(200);

      items.push({
        name,
        mealPeriod: "any",
        calories: Math.min(2000, calories),
        protein: Math.min(150, protein),
        carbs: Math.min(200, carbs),
        fat: Math.min(200, fat),
      });
    }
  } finally {
    await browser.close();
  }

  return items;
}
