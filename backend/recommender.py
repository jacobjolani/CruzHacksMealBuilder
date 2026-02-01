from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NutritionTotals:
    calories: float = 0.0
    fat: float = 0.0
    carbs: float = 0.0
    protein: float = 0.0


def _to_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0


def calculate_totals(items: list[dict[str, Any]]) -> NutritionTotals:
    cals = fat = carbs = prot = 0.0
    for it in items:
        cals += _to_float(it.get("calories", 0))
        fat += _to_float(it.get("fat", 0))
        carbs += _to_float(it.get("carbs", 0))
        prot += _to_float(it.get("protein", 0))
    return NutritionTotals(calories=cals, fat=fat, carbs=carbs, protein=prot)


def recommend_meal_plan_rule_based(
    menu: list[dict[str, Any]],
    goal: str,
    target_amount: float,
    *,
    max_items: int = 5,
    tolerance: float = 10.0,
) -> dict[str, Any]:
    """
    Rule-based optimization heuristic:
    - Filter candidates to items that contribute to the goal nutrient.
    - Greedily add the item that most reduces absolute error vs target.
    - Stop when within tolerance or max_items reached.
    """
    goal = goal.lower().strip()
    if goal in {"carbohydrates"}:
        goal = "carbs"
    if goal in {"fats"}:
        goal = "fat"

    if goal not in {"protein", "carbs", "fat", "calories"}:
        raise ValueError("Invalid goal")

    def nutrient_value(it: dict[str, Any]) -> float:
        return _to_float(it.get(goal, 0))

    candidates = [it for it in menu if nutrient_value(it) > 0]
    if not candidates:
        return {"meal_items": [], "total_nutrition": calculate_totals([]).__dict__, "note": "No suitable items found."}

    chosen: list[dict[str, Any]] = []
    current = 0.0

    # Greedy improvement loop
    for _ in range(max_items):
        best = None
        best_err = None
        for it in candidates:
            v = nutrient_value(it)
            if v <= 0:
                continue
            new_val = current + v
            err = abs(target_amount - new_val)
            if best_err is None or err < best_err:
                best = it
                best_err = err
        if best is None:
            break

        chosen.append(best)
        current += nutrient_value(best)

        if abs(target_amount - current) <= tolerance:
            break

    totals = calculate_totals(chosen)
    return {
        "meal_items": chosen,
        "total_nutrition": totals.__dict__,
        "target": {"nutrient": goal, "amount": target_amount, "tolerance": tolerance, "max_items": max_items},
    }

