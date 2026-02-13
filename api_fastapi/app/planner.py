"""
Rule-based meal optimizer: greedy selection to meet nutritional targets.
Partitions by meal_period; fills each slot to approach target/3 for calories/protein/carbs/fat.
"""
import random
from typing import Any

TOLERANCE = 0.05
MAX_ITEMS_PER_MEAL = 5
WEIGHTS = {"protein": 4, "carbs": 2, "fat": 1, "calories": 0.5}


def _slot_error(
    current: dict[str, float],
    slot_targets: dict[str, float],
) -> float:
    err = 0.0
    for k, target in slot_targets.items():
        if target <= 0:
            continue
        c = current.get(k, 0)
        diff = c - target
        norm = max(target, 1.0)
        overshoot = 1.5 if k in ("calories", "fat", "carbs") else 1.0
        if diff > 0:
            err += (overshoot * (diff / norm)) * WEIGHTS.get(k, 1)
        else:
            err += (abs(diff) / norm) * WEIGHTS.get(k, 1)
    return err


def _fill_slot(
    items: list[dict[str, Any]],
    slot_targets: dict[str, float],
    used_ids: set[int],
) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    current = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}

    for _ in range(MAX_ITEMS_PER_MEAL):
        if _slot_error(current, slot_targets) <= TOLERANCE:
            break
        best_candidates: list[dict[str, Any]] = []
        best_err = float("inf")

        for it in items:
            if it["id"] in used_ids:
                continue
            trial = {
                "calories": current["calories"] + it["calories"],
                "protein": current["protein"] + it["protein"],
                "carbs": current["carbs"] + it["carbs"],
                "fat": current["fat"] + it["fat"],
            }
            err = _slot_error(trial, slot_targets)
            if err < best_err:
                best_err = err
                best_candidates = [it]
            elif err == best_err:
                best_candidates.append(it)

        if not best_candidates:
            break
        best = random.choice(best_candidates)
        chosen.append(best)
        used_ids.add(best["id"])
        current = {
            "calories": current["calories"] + best["calories"],
            "protein": current["protein"] + best["protein"],
            "carbs": current["carbs"] + best["carbs"],
            "fat": current["fat"] + best["fat"],
        }

    return chosen


def build_plan(
    items: list[dict[str, Any]],
    targets: dict[str, float],
) -> dict[str, Any]:
    """Rule-based optimization over nutritional targets. Returns breakfast, lunch, dinner + totals + deltas."""
    slot_targets = {k: v / 3.0 for k, v in targets.items() if v and v > 0}
    if not slot_targets:
        slot_targets = {"calories": 2000 / 3, "protein": 50, "carbs": 60, "fat": 22}

    breakfast_pool = [i for i in items if i.get("meal_period") in ("breakfast", "any")]
    lunch_pool = [i for i in items if i.get("meal_period") in ("lunch", "any")]
    dinner_pool = [i for i in items if i.get("meal_period") in ("dinner", "any")]
    fallback = items if items else []
    brunch = breakfast_pool or fallback
    lunch_items = lunch_pool or fallback
    dinner_items = dinner_pool or fallback

    random.shuffle(brunch)
    random.shuffle(lunch_items)
    random.shuffle(dinner_items)

    used: set[int] = set()

    def sum_items(its: list[dict]) -> dict[str, float]:
        return {
            "calories": sum(x["calories"] for x in its),
            "protein": sum(x["protein"] for x in its),
            "carbs": sum(x["carbs"] for x in its),
            "fat": sum(x["fat"] for x in its),
        }

    b = _fill_slot(brunch, slot_targets, used)
    lunch_slot = _fill_slot(lunch_items, slot_targets, used)
    d = _fill_slot(dinner_items, slot_targets, used)

    breakfast = {"items": b, **sum_items(b)}
    lunch = {"items": lunch_slot, **sum_items(lunch_slot)}
    dinner = {"items": d, **sum_items(d)}

    totals = {
        "calories": breakfast["calories"] + lunch["calories"] + dinner["calories"],
        "protein": breakfast["protein"] + lunch["protein"] + dinner["protein"],
        "carbs": breakfast["carbs"] + lunch["carbs"] + dinner["carbs"],
        "fat": breakfast["fat"] + lunch["fat"] + dinner["fat"],
    }
    deltas = {
        "calories": (targets.get("calories") or 0) - totals["calories"],
        "protein": (targets.get("protein") or 0) - totals["protein"],
        "carbs": (targets.get("carbs") or 0) - totals["carbs"],
        "fat": (targets.get("fat") or 0) - totals["fat"],
    }
    return {"breakfast": breakfast, "lunch": lunch, "dinner": dinner, "totals": totals, "deltas": deltas}
