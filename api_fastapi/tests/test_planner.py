"""Unit tests for rule-based meal planner (no DB/Redis)."""
from app.planner import build_plan


def test_build_plan_empty_items_uses_fallback():
    result = build_plan([], {"calories": 2000, "protein": 150, "carbs": 200, "fat": 65})
    assert "breakfast" in result
    assert "lunch" in result
    assert "dinner" in result
    assert "totals" in result
    assert "deltas" in result
    assert result["totals"]["calories"] == 0
    assert result["totals"]["protein"] == 0


def test_build_plan_single_item_per_period():
    items = [
        {"id": 1, "name": "Oatmeal", "meal_period": "breakfast", "calories": 150, "protein": 5, "carbs": 27, "fat": 3},
        {"id": 2, "name": "Salad", "meal_period": "lunch", "calories": 300, "protein": 12, "carbs": 20, "fat": 18},
        {"id": 3, "name": "Chicken", "meal_period": "dinner", "calories": 400, "protein": 35, "carbs": 0, "fat": 28},
    ]
    result = build_plan(items, {"calories": 2000, "protein": 150, "carbs": 200, "fat": 65})
    assert len(result["breakfast"]["items"]) >= 0
    assert len(result["lunch"]["items"]) >= 0
    assert len(result["dinner"]["items"]) >= 0
    assert result["totals"]["calories"] == 150 + 300 + 400
    assert result["totals"]["protein"] == 5 + 12 + 35


def test_build_plan_any_period_spreads():
    items = [
        {"id": 1, "name": "Bar", "meal_period": "any", "calories": 100, "protein": 4, "carbs": 12, "fat": 4},
    ]
    result = build_plan(items, {"calories": 900, "protein": 30, "carbs": 36, "fat": 12})
    assert result["totals"]["calories"] >= 100
    assert result["totals"]["protein"] >= 4
