import { describe, it, expect } from "vitest";
import { buildPlan, type MenuItemRow } from "./planner.js";

const item = (id: string, name: string, cal: number, p: number, c: number, f: number, period = "any"): MenuItemRow => ({
  id,
  name,
  mealPeriod: period,
  calories: cal,
  protein: p,
  carbs: c,
  fat: f,
});

describe("buildPlan", () => {
  it("returns three meals with totals and deltas", () => {
    const items: MenuItemRow[] = [
      item("1", "Eggs", 150, 12, 1, 10, "breakfast"),
      item("2", "Oatmeal", 200, 6, 35, 4, "breakfast"),
      item("3", "Chicken", 250, 30, 0, 14, "lunch"),
      item("4", "Rice", 180, 4, 38, 0, "lunch"),
      item("5", "Salmon", 280, 25, 0, 18, "dinner"),
      item("6", "Broccoli", 50, 4, 10, 0, "dinner"),
    ];

    const result = buildPlan(items, {
      calories: 1000,
      protein: 80,
      carbs: 100,
      fat: 40,
    });

    expect(result.breakfast.items.length).toBeGreaterThan(0);
    expect(result.lunch.items.length).toBeGreaterThan(0);
    expect(result.dinner.items.length).toBeGreaterThan(0);
    expect(result.totals.calories).toBe(
      result.breakfast.calories + result.lunch.calories + result.dinner.calories
    );
    expect(result.totals.protein).toBe(
      result.breakfast.protein + result.lunch.protein + result.dinner.protein
    );
    expect(result.deltas).toHaveProperty("calories");
    expect(result.deltas).toHaveProperty("protein");
  });

  it("uses all items when no mealPeriod partition", () => {
    const items: MenuItemRow[] = [
      item("1", "A", 100, 10, 10, 5),
      item("2", "B", 100, 10, 10, 5),
      item("3", "C", 100, 10, 10, 5),
    ];

    const result = buildPlan(items, { protein: 25, calories: 250 });
    expect(result.breakfast.items.length + result.lunch.items.length + result.dinner.items.length).toBeGreaterThan(0);
    expect(result.totals.protein).toBeGreaterThan(0);
  });

  it("stops without blowing past targets", () => {
    const items: MenuItemRow[] = [
      item("1", "Small", 50, 5, 5, 2),
      item("2", "Small2", 50, 5, 5, 2),
      item("3", "Small3", 50, 5, 5, 2),
    ];

    const result = buildPlan(items, { calories: 120, protein: 12 });
    expect(result.totals.calories).toBeLessThanOrEqual(200);
    expect(result.totals.protein).toBeLessThanOrEqual(20);
  });
});
