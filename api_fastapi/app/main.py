import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.cache import cache_get_json, cache_set_json, cache_stats
from app.config import settings
from app.database import get_db
from app.models import MenuDay, UserProfile
from app.planner import build_plan
from pydantic import BaseModel

from app.schemas import HealthResponse, PlanResponse, PlanTargets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MENU_CACHE_KEY = "menu:today"
MENU_TTL = 3600
PLAN_CACHE_PREFIX = "plan:"
PLAN_TTL = 300


def _targets_from_body(body: PlanTargets | None) -> dict[str, float]:
    t: dict[str, float] = {}
    if body:
        if body.daily_calories is not None:
            t["calories"] = body.daily_calories
        if body.daily_protein is not None:
            t["protein"] = body.daily_protein
        if body.daily_carbs is not None:
            t["carbs"] = body.daily_carbs
        if body.daily_fat is not None:
            t["fat"] = body.daily_fat
    return t


def _plan_cache_key(session_id: str, targets: dict[str, float]) -> str:
    parts = sorted(f"{k}:{v}" for k, v in targets.items())
    return f"{PLAN_CACHE_PREFIX}{session_id}:{':'.join(parts)}"


def _ensure_sqlite_seeded():
    """When using SQLite, create tables and seed today's menu so the app works without Docker."""
    from datetime import date, datetime
    from app.database import Base, SessionLocal, engine
    from app.models import MenuDay, MenuItem
    if "sqlite" not in settings.database_url:
        return
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        today = date.today().isoformat()
        if db.query(MenuDay).filter(MenuDay.date == today).first():
            return
        menu_day = MenuDay(date=today, scraped_at=datetime.utcnow())
        db.add(menu_day)
        db.flush()
        for name, period, cal, pro, carb, fat in [
            ("Oatmeal", "breakfast", 150, 5, 27, 3), ("Eggs", "breakfast", 200, 14, 2, 15),
            ("Salad", "lunch", 300, 12, 20, 18), ("Grilled Chicken", "lunch", 400, 35, 0, 22),
            ("Pasta", "dinner", 450, 15, 60, 12), ("Salmon", "dinner", 380, 34, 0, 24),
        ]:
            db.add(MenuItem(menu_day_id=menu_day.id, name=name, meal_period=period, calories=cal, protein=pro, carbs=carb, fat=fat))
        db.commit()
        logger.info("Seeded today's menu for SQLite (no-Docker mode)")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_sqlite_seeded()
    yield
    # shutdown if needed


app = FastAPI(title="NutriOpt API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        database=db_status,
        cache=cache_stats(),
    )


@app.get("/api/menu/today")
def menu_today(db: Session = Depends(get_db)):
    cached = cache_get_json(MENU_CACHE_KEY)
    if cached is not None:
        return cached
    from datetime import date
    today = date.today().isoformat()
    menu_day = db.query(MenuDay).filter(MenuDay.date == today).first()
    if not menu_day:
        return {"date": today, "items": [], "message": "No menu for today. Seed or scrape first."}
    items = [
        {
            "id": m.id,
            "name": m.name,
            "meal_period": m.meal_period,
            "calories": m.calories,
            "protein": m.protein,
            "carbs": m.carbs,
            "fat": m.fat,
        }
        for m in menu_day.menu_items
    ]
    out = {"date": today, "items": items}
    cache_set_json(MENU_CACHE_KEY, out, MENU_TTL)
    return out


@app.post("/api/plan", response_model=PlanResponse)
def plan(
    body: PlanTargets | None = None,
    db: Session = Depends(get_db),
    x_session_id: str | None = Header(None, alias="X-Session-Id"),
):
    session_id = x_session_id or ""
    from datetime import date
    today = date.today().isoformat()
    targets = _targets_from_body(body)
    if not targets:
        profile = db.query(UserProfile).filter(UserProfile.session_id == session_id).first() if session_id else None
        if profile:
            if profile.daily_calories is not None:
                targets["calories"] = profile.daily_calories
            if profile.daily_protein is not None:
                targets["protein"] = profile.daily_protein
            if profile.daily_carbs is not None:
                targets["carbs"] = profile.daily_carbs
            if profile.daily_fat is not None:
                targets["fat"] = profile.daily_fat
    if not targets:
        targets = {"calories": 2000, "protein": 150, "carbs": 200, "fat": 65}

    cache_key = _plan_cache_key(session_id or "anon", targets)
    cached = cache_get_json(cache_key)
    if cached is not None:
        return cached

    menu_day = db.query(MenuDay).filter(MenuDay.date == today).first()
    if not menu_day or not menu_day.menu_items:
        raise HTTPException(status_code=404, detail="No menu for today. Seed or scrape first.")

    items = [
        {
            "id": m.id,
            "name": m.name,
            "meal_period": m.meal_period,
            "calories": m.calories,
            "protein": m.protein,
            "carbs": m.carbs,
            "fat": m.fat,
        }
        for m in menu_day.menu_items
    ]
    logger.info("plan targets=%s menu_items=%d", targets, len(items))
    result = build_plan(items, targets)
    cache_set_json(cache_key, result, PLAN_TTL)
    return result


class ProfileUpdate(BaseModel):
    session_id: str
    daily_calories: float | None = None
    daily_protein: float | None = None
    daily_carbs: float | None = None
    daily_fat: float | None = None


@app.post("/api/profile")
def profile_post(payload: ProfileUpdate, db: Session = Depends(get_db)):
    session_id = payload.session_id
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    from datetime import datetime
    profile = db.query(UserProfile).filter(UserProfile.session_id == session_id).first()
    if profile:
        if payload.daily_calories is not None:
            profile.daily_calories = payload.daily_calories
        if payload.daily_protein is not None:
            profile.daily_protein = payload.daily_protein
        if payload.daily_carbs is not None:
            profile.daily_carbs = payload.daily_carbs
        if payload.daily_fat is not None:
            profile.daily_fat = payload.daily_fat
        profile.updated_at = datetime.utcnow()
    else:
        profile = UserProfile(
            session_id=session_id,
            daily_calories=payload.daily_calories,
            daily_protein=payload.daily_protein,
            daily_carbs=payload.daily_carbs,
            daily_fat=payload.daily_fat,
        )
        db.add(profile)
    db.commit()
    return {"ok": True}


@app.get("/api/profile")
def profile_get(session_id: str = "", db: Session = Depends(get_db)):
    if not session_id:
        return {"profile": None}
    profile = db.query(UserProfile).filter(UserProfile.session_id == session_id).first()
    if not profile:
        return {"profile": None}
    return {"profile": {"daily_calories": profile.daily_calories, "daily_protein": profile.daily_protein, "daily_carbs": profile.daily_carbs, "daily_fat": profile.daily_fat}}
