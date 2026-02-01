from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class MealGenerateRequest(BaseModel):
    goal: str = Field(description="protein|carbs|fat|calories")
    target_amount: float = Field(gt=0)
    max_items: int = Field(default=5, ge=1, le=10)
    tolerance: float = Field(default=10.0, gt=0)


class MealGenerateResponse(BaseModel):
    meal_items: list[dict[str, Any]]
    total_nutrition: dict[str, float]
    target: dict[str, Any]
    cached: bool = False


class MealPlanPublic(BaseModel):
    id: int
    goal: str
    target_amount: float
    total_nutrition: dict[str, Any]
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    database: str
    cache: dict[str, Any]
    timestamp: float


class CacheStatsResponse(BaseModel):
    enabled: bool
    hits: int
    misses: int
    hit_rate: Optional[float]
    timestamp: float

