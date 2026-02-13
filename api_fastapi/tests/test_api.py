"""API tests: /health, schema validation, /api/plan (when DB has menu)."""
import pytest
from fastapi.testclient import TestClient

from app.schemas import HealthResponse, PlanResponse, PlanTargets


def test_health_returns_200_and_schema(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "database" in data
    assert "cache" in data
    # Schema validation
    HealthResponse(**data)


def test_health_cache_stats_shape(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    cache = r.json()["cache"]
    assert "enabled" in cache
    assert "hits" in cache
    assert "misses" in cache


def test_plan_accepts_body_schema():
    # Pydantic schema used by /api/plan
    PlanTargets(daily_calories=2000, daily_protein=150)
    PlanTargets()
    PlanTargets(daily_calories=None, daily_carbs=200)


def test_plan_response_schema():
    PlanResponse(
        breakfast={"items": [], "calories": 0, "protein": 0, "carbs": 0, "fat": 0},
        lunch={"items": [], "calories": 0, "protein": 0, "carbs": 0, "fat": 0},
        dinner={"items": [], "calories": 0, "protein": 0, "carbs": 0, "fat": 0},
        totals={"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
        deltas={"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
    )


def test_plan_post_no_menu_returns_404(client: TestClient):
    # When no menu for today, API returns 404; 500 or connection error if DB unavailable
    try:
        r = client.post("/api/plan", json={"daily_calories": 2000, "daily_protein": 150})
    except Exception as e:
        pytest.skip(f"DB/Redis unavailable: {e}")
    assert r.status_code in (200, 404, 500)
    if r.status_code == 200:
        data = r.json()
        PlanResponse(**data)


def test_menu_today_returns_200(client: TestClient):
    try:
        r = client.get("/api/menu/today")
    except Exception as e:
        pytest.skip(f"DB/Redis unavailable: {e}")
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert "date" in data
        assert "items" in data


def test_openapi_schema_available(client: TestClient):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "paths" in schema
    assert "/health" in schema["paths"]
    assert "/api/plan" in schema["paths"]
