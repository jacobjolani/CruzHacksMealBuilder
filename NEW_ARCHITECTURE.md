# New Architecture — Meal Planner MVP

## Step A: Audit — What to Delete / Keep

### DELETE (entirely)
- **`app.py`** — Flask app; replaced by Node/Express API.
- **`backend/`** — FastAPI + Python recommender/cache/db; replaced by API + planner.
- **`models.py`** — Flask-SQLAlchemy models; replaced by Prisma schema.
- **`init_db.py`** — Python DB init; replaced by Prisma migrate.
- **`algorithm.py`** — Python meal logic; replaced by TypeScript planner.
- **`macros scraper.py`** — Selenium scraper; replaced by Playwright/Cheerio in API.
- **`templates/`** — Flask HTML; replaced by Next.js.
- **`static/`** — Flask static JS/CSS; replaced by Next.js.
- **`script.js`**, **`style.css`** (root) — Duplicates; gone with Flask.
- **`tests/`** — Python pytest; replaced by Node tests for planner/API.
- **`requirements.txt`**, **`Dockerfile`**, **`docker-compose.yml`**, **`app.yaml`** — Python/Docker; new stack uses Node/Docker later if needed.
- **`.github/workflows/ci.yml`** — Python CI; replace with Node CI when added.
- **`.flake8`**, **`pytest.ini`**, **`pyproject.toml`** — Python tooling; not used.
- **`env.example`** — Python env; new one for API.
- **`Cafe3_brunch.json`**, **`Cafe3_dinner.json`** — Static menu data; scraper will populate DB (can delete after scraper works).
- **`logs/`** — Flask logs; not carried over.

### KEEP (then update)
- **`.gitignore`** — Update for Node (node_modules, .env, build, Prisma, etc.).
- **`README.md`** — Replace with new run instructions and MVP description.

### WHY
- Single language/runtime (TypeScript) for backend + frontend; one package manager; no dual Flask/FastAPI or Python/Node split.
- Prisma gives SQLite now and Postgres path later with one schema.
- Next.js App Router + Tailwind gives a single, deployable frontend.
- Scraper lives inside API as a clear adapter; daily cron + manual trigger.

---

## Step B: Final Folder Structure

```
/
├── NEW_ARCHITECTURE.md
├── README.md
├── .gitignore
├── package.json                 # root workspace scripts
├── api/                         # Express + TypeScript backend
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts
│   │   ├── routes/
│   │   │   ├── profile.ts
│   │   │   ├── scrape.ts
│   │   │   ├── menu.ts
│   │   │   └── plan.ts
│   │   ├── services/
│   │   │   ├── scraper.ts       # Berkeley menu adapter
│   │   │   ├── planner.ts       # deterministic meal builder
│   │   │   └── cache.ts         # day-level plan cache
│   │   └── lib/
│   │       └── prisma.ts
│   └── prisma/
│       ├── schema.prisma
│       └── migrations/
├── web/                         # Next.js App Router frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── app/
│       ├── layout.tsx
│       ├── page.tsx             # landing + set targets
│       ├── plan/
│       │   └── page.tsx         # plan view, regenerate, swap
│       └── globals.css
└── (no Python, no backend/, no templates/)
```

---

## How to Run

- **Backend:** `npm run dev:api` (or `cd api && npm run dev`) — Express on port 4000.
- **Frontend:** `npm run dev:web` (or `cd web && npm run dev`) — Next.js on port 3000.
- **DB:** SQLite file at `api/prisma/dev.db`. First run: `cd api && npx prisma migrate dev`.
- **Single dev (both):** `npm run dev` (concurrently) from root.

---

## Key Decisions

1. **Monorepo, two apps** — `api/` and `web/` under one repo; root `package.json` runs both.
2. **SQLite + Prisma** — Dev uses SQLite; swap `url` to Postgres for production.
3. **Session-based profile** — No auth; session ID (cookie) ties to `UserProfile` and `MealPlan`.
4. **Scraper in API** — `services/scraper.ts` is the only place that knows Berkeley DOM; easy to swap selector/adapter if site changes.
5. **Deterministic planner** — Greedy/knapsack-style; no LLM for core planning. Priority: hit macros (protein, then carbs, then fat, then calories) without overshooting.
6. **Cache by day** — One scrape per calendar day; plan generation reads from DB and can cache plan per (day, profile) to avoid recompute for same inputs.
