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

## NutriOpt (Resume stack) — FastAPI + PostgreSQL + Redis

This repo includes a **Python/FastAPI** service that backs the resume line:  
*NutriOpt (Hackathon) | Python, FastAPI, PostgreSQL, Redis, AWS, Docker, REST.*

### Run locally (under 5 minutes)

```bash
docker compose up --build
```

Then:

- **API:** http://localhost:8000  
- **Health:** http://localhost:8000/health  
- **Meal plan:** `curl -X POST http://localhost:8000/api/plan -H "Content-Type: application/json" -d '{"daily_calories":2000,"daily_protein":150}'`  
- **OpenAPI:** http://localhost:8000/docs  

Containers: `api` (FastAPI), `postgres`, `redis`. Migrations and a one-time seed for today’s menu run on startup.

### Architecture justification for resume claims

| Claim | Where it lives | How it works |
|-------|----------------|--------------|
| **REST API with meal recommendations via rule-based optimization** | `api_fastapi/app/main.py` (`POST /api/plan`), `api_fastapi/app/planner.py` | `/api/plan` accepts nutritional targets (or uses profile); `build_plan()` does greedy, rule-based selection by meal period to meet targets; returns breakfast/lunch/dinner + totals + deltas. |
| **FastAPI + PostgreSQL as primary DB** | `api_fastapi/app/main.py`, `api_fastapi/app/database.py`, `api_fastapi/app/models.py` | FastAPI app with SQLAlchemy; all menu, profile, and plan data read/written via PostgreSQL. |
| **Redis for caching to reduce latency** | `api_fastapi/app/cache.py`, `api_fastapi/app/main.py` | Menu for today cached at `menu:today` (TTL 1h); plan results cached by `plan:{session_id}:{targets}` (TTL 5 min). Cache used in `GET /api/menu/today` and `POST /api/plan`. |
| **PostgreSQL queries indexed and optimized** | `api_fastapi/app/models.py`, `api_fastapi/alembic/versions/001_initial.py` | Indexes: `menu_days.date`, `menu_items(menu_day_id, meal_period)`, `user_profiles(session_id, updated_at)`, `meal_plans(session_id, created_at)`. Migrations create them. |
| **Redis cache hit/miss strategy** | `api_fastapi/app/cache.py` | On every get: `cache:hits` or `cache:misses` incremented; `cache_stats()` returns hits, misses, hit_rate; every hit/miss is logged (key, hits, misses). Exposed in `GET /health` under `cache`. |
| **CI/CD: automated tests, schema validation, reproducible builds** | `.github/workflows/ci.yml`, `api_fastapi/tests/` | GitHub Actions: install deps, run migrations, **ruff** lint, **pytest** (unit + API tests). Pydantic schemas validated in tests (`HealthResponse`, `PlanResponse`, `PlanTargets`). Reproducible build via Docker. |
| **System Dockerized** | `api_fastapi/Dockerfile`, `docker-compose.yml` | Single Dockerfile for the API; `docker-compose.yml` defines `api`, `postgres`, `redis` with healthchecks; `docker compose up` runs the stack. |
| **Deployable to AWS EC2** | This README + Docker | Run `docker compose` on an EC2 instance (or use the same Dockerfile in ECS/App Runner). Documented: install Docker, clone repo, set `DATABASE_URL`/`REDIS_URL` if not using local Postgres/Redis, then `docker compose up`. No mock or placeholder; same image runs locally and on EC2. |

### API (FastAPI)

- `GET /health` — Health check; returns DB status and Redis cache stats (hits, misses, hit_rate).
- `GET /api/menu/today` — Today’s menu (cached).
- `POST /api/plan` — Rule-based meal plan. Body: optional `daily_calories`, `daily_protein`, `daily_carbs`, `daily_fat`; optional header `X-Session-Id` to use saved profile. Response: breakfast/lunch/dinner + totals + deltas (cached by targets).
- `POST /api/profile` — Body: `session_id`, optional macro fields. Create/update profile.
- `GET /api/profile?session_id=...` — Get profile by session.

### Run tests / lint (no Docker)

From repo root, with PostgreSQL and Redis available (or use CI):

```bash
cd api_fastapi
pip install -r requirements.txt -r requirements-dev.txt
export DATABASE_URL=postgresql://user:password@localhost:5432/mealplanner REDIS_URL=redis://localhost:6379/0
alembic upgrade head
ruff check app tests
pytest tests -v
```

## New architecture

See **NEW_ARCHITECTURE.md** for audit, folder structure, and decisions.
