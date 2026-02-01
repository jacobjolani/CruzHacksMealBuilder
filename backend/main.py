import json
import os
import time
from datetime import datetime
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.cache import cache_get_json, cache_set_json, cache_stats, get_redis
from backend.config import settings
from backend.db import Base, engine, get_db
from backend.models import MealPlan, MenuItem, User
from backend.recommender import recommend_meal_plan_rule_based
from backend.schemas import (
    CacheStatsResponse,
    HealthResponse,
    LoginRequest,
    MealGenerateRequest,
    MealGenerateResponse,
    MealPlanPublic,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from backend.security import create_access_token, get_password_hash, verify_password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _current_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _repo_root() -> str:
    return os.path.dirname(_current_dir())


def _load_menu_json_fallback() -> list[dict[str, Any]]:
    root = _repo_root()
    brunch_path = os.path.join(root, "Cafe3_brunch.json")
    dinner_path = os.path.join(root, "Cafe3_dinner.json")
    with open(brunch_path, "r") as f1:
        brunch = json.load(f1)
    with open(dinner_path, "r") as f2:
        dinner = json.load(f2)
    return brunch + dinner


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_id = int(sub)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


app = FastAPI(
    title="CruzHacks Meal Builder API",
    version="1.0.0",
    description="FastAPI service for meal recommendations with PostgreSQL + Redis caching.",
)


@app.on_event("startup")
def _startup() -> None:
    # Create tables (for production, you should use migrations; this keeps the repo runnable).
    Base.metadata.create_all(bind=engine)


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health(db: Session = Depends(get_db)) -> dict[str, Any]:
    # DB check
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    # Cache check
    r = get_redis()
    cache_enabled = bool(r is not None)
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "cache": {**cache_stats(), "enabled": cache_enabled},
        "timestamp": time.time(),
    }


@app.get("/cache/stats", response_model=CacheStatsResponse, tags=["ops"])
def cache_stats_endpoint() -> dict[str, Any]:
    return cache_stats()


@app.post("/auth/register", response_model=UserPublic, status_code=201, tags=["auth"])
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        username=payload.username,
        email=str(payload.email),
        password_hash=get_password_hash(payload.password),
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email, "created_at": user.created_at}


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserPublic, tags=["users"])
def me(user: User = Depends(get_current_user)) -> dict[str, Any]:
    return {"id": user.id, "username": user.username, "email": user.email, "created_at": user.created_at}


def _menu_from_db(db: Session) -> list[dict[str, Any]]:
    items = db.query(MenuItem).all()
    return [
        {
            "food_name": it.food_name,
            "calories": float(it.calories),
            "fat": float(it.fat),
            "carbs": float(it.carbs),
            "protein": float(it.protein),
            "meal_type": it.meal_type,
        }
        for it in items
    ]


@app.post("/meal/generate", response_model=MealGenerateResponse, tags=["meal"])
def generate_meal(
    payload: MealGenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    cache_key = f"meal:gen:v1:user:{user.id}:goal:{payload.goal}:target:{payload.target_amount}:max:{payload.max_items}:tol:{payload.tolerance}"
    cached = cache_get_json(cache_key)
    if cached is not None:
        cached["cached"] = True
        return cached

    # Menu is a hot read; keep it cacheable separately
    menu_cache_key = "menu:items:v1"
    menu = cache_get_json(menu_cache_key)
    if menu is None:
        menu = _menu_from_db(db)
        if not menu:
            # Fallback for first-run demos; production should seed Postgres
            menu = _load_menu_json_fallback()
        cache_set_json(menu_cache_key, menu, ttl_seconds=3600)

    try:
        result = recommend_meal_plan_rule_based(
            menu,
            payload.goal,
            payload.target_amount,
            max_items=payload.max_items,
            tolerance=payload.tolerance,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid goal; must be protein|carbs|fat|calories")

    # Persist plan
    plan = MealPlan(
        user_id=user.id,
        goal=payload.goal.lower(),
        target_amount=float(payload.target_amount),
        meal_items=result.get("meal_items", []),
        total_nutrition=result.get("total_nutrition", {}),
        created_at=datetime.utcnow(),
    )
    db.add(plan)
    db.commit()

    response = {**result, "cached": False}
    cache_set_json(cache_key, response, ttl_seconds=settings.CACHE_TTL_SECONDS)
    return response


@app.get("/meal/plans", response_model=list[MealPlanPublic], tags=["meal"])
def list_meal_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    plans = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == user.id)
        .order_by(MealPlan.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": p.id,
            "goal": p.goal,
            "target_amount": float(p.target_amount),
            "total_nutrition": p.total_nutrition,
            "created_at": p.created_at,
        }
        for p in plans
    ]

