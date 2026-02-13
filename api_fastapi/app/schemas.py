from typing import Any, Optional
from pydantic import BaseModel, Field


class PlanTargets(BaseModel):
    daily_calories: Optional[float] = Field(None, gt=0)
    daily_protein: Optional[float] = Field(None, gt=0)
    daily_carbs: Optional[float] = Field(None, gt=0)
    daily_fat: Optional[float] = Field(None, gt=0)


class PlanResponse(BaseModel):
    breakfast: dict[str, Any]
    lunch: dict[str, Any]
    dinner: dict[str, Any]
    totals: dict[str, float]
    deltas: dict[str, float]


class HealthResponse(BaseModel):
    status: str
    database: str
    cache: dict[str, Any]
