# Meal Planner MVP

Automated meal planner: UC Berkeley dining menu → 3 daily meals (breakfast, lunch, dinner) that meet your macro targets. Session-based; no auth.

## Stack

- **API:** Node.js, Express, TypeScript, Prisma, SQLite (path to Postgres), Playwright scraper, node-cron daily scrape.
- **Web:** Next.js 15 (App Router), TypeScript, Tailwind.

## Run locally

### One-time setup

```bash
# Install root + api + web
npm install
cd api && npm install && cd ..
cd web && npm install && cd ..

# Database (SQLite)
cd api
cp .env.example .env
npx prisma generate
npx prisma db push
npm run db:seed
cd ..
```

### Dev (two terminals)

**Terminal 1 — API (port 4000):**
```bash
npm run dev:api
```

**Terminal 2 — Web (port 3000):**
```bash
npm run dev:web
```

Then open **http://localhost:3000**. Set targets on `/`, then go to `/plan` to generate and view today’s meals.

### Single command (both)

```bash
npm run dev
```

(Requires `concurrently`; install with `npm install` at root.)

## Env

- **api/.env:** `DATABASE_URL="file:./prisma/dev.db"`, `PORT=4000`, optional `BERKELEY_MENU_URL`.
- **web:** Optional `NEXT_PUBLIC_API_URL=http://localhost:4000` (default for local).

## API (minimal)

- `POST /api/profile` — Save targets (session cookie set by middleware).
- `GET  /api/profile` — Get current profile.
- `GET  /api/menu/today` — Today’s menu items (or `?date=YYYY-MM-DD`).
- `POST /api/scrape/run` — Manual scrape (dev); idempotent for the day.
- `POST /api/plan/generate` — Generate 3 meals; body: `dailyCalories`, `dailyProtein`, `dailyCarbs`, `dailyFat`.
- `POST /api/plan/regenerate?meal=breakfast|lunch|dinner` — Regenerate one meal.
- `POST /api/plan/swap` — Body: `meal`, `outItemId`, `inItemId` (swap one item in a meal).

## Scraper

Berkeley menu is scraped via Playwright in `api/src/services/scraper.ts`. Selectors are isolated so they can be updated if the site changes. Daily cron runs at 5 AM; use `POST /api/scrape/run` for manual run. **First run without scraper:** use `npm run db:seed` in `api` to load sample menu for today. If you use the live scraper, install Chromium once: `cd api && npx playwright install chromium`.

## New architecture

See **NEW_ARCHITECTURE.md** for audit, folder structure, and decisions.
