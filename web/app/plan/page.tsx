"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:4000";

type MenuItem = { id: string; name: string; calories: number; protein: number; carbs: number; fat: number };
type Meal = { items: MenuItem[]; calories: number; protein: number; carbs: number; fat: number };
type Plan = {
  date: string;
  breakfast: Meal;
  lunch: Meal;
  dinner: Meal;
  totals: { calories: number; protein: number; carbs: number; fat: number };
  deltas: { calories: number; protein: number; carbs: number; fat: number };
};

export default function PlanPage() {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [menu, setMenu] = useState<{ items: MenuItem[]; date: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadMenu = () => {
    fetch(`${API}/api/menu/today`, { credentials: "include" })
      .then((r) => r.json())
      .then((d) => setMenu({ items: d.items ?? [], date: d.date ?? "" }))
      .catch(() => setMenu({ items: [], date: "" }));
  };

  useEffect(() => {
    loadMenu();
    fetch(`${API}/api/profile`, { credentials: "include" })
      .then((r) => r.json())
      .then((d) => {
        const p = d.profile;
        if (p && (p.dailyProtein != null || p.dailyCalories != null)) {
          return fetch(`${API}/api/plan/generate`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              dailyCalories: p.dailyCalories,
              dailyProtein: p.dailyProtein,
              dailyCarbs: p.dailyCarbs,
              dailyFat: p.dailyFat,
            }),
          });
        }
        setLoading(false);
        return null;
      })
      .then((r) => {
        if (r && r.ok) return r.json();
        setLoading(false);
        return null;
      })
      .then((data) => {
        if (data && !data.error) {
          setPlan(data);
          setError(null);
        }
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message ?? "Failed to load");
        setLoading(false);
      });
  }, []);

  const generate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const prof = await fetch(`${API}/api/profile`, { credentials: "include" }).then((r) => r.json());
      const p = prof.profile ?? {};
      const res = await fetch(`${API}/api/plan/generate`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dailyCalories: p.dailyCalories,
          dailyProtein: p.dailyProtein,
          dailyCarbs: p.dailyCarbs,
          dailyFat: p.dailyFat,
        }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.message ?? data.error);
      setPlan(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generate failed");
    } finally {
      setGenerating(false);
    }
  };

  const regenerateMeal = async (meal: string) => {
    if (!plan) return;
    setGenerating(true);
    setError(null);
    try {
      const prof = await fetch(`${API}/api/profile`, { credentials: "include" }).then((r) => r.json());
      const p = prof.profile ?? {};
      const res = await fetch(
        `${API}/api/plan/regenerate?meal=${meal}`,
        {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            date: plan.date,
            dailyCalories: p.dailyCalories,
            dailyProtein: p.dailyProtein,
            dailyCarbs: p.dailyCarbs,
            dailyFat: p.dailyFat,
          }),
        }
      );
      const data = await res.json();
      if (data.error) throw new Error(data.message ?? data.error);
      setPlan(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Regenerate failed");
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <p className="text-slate-500">Loading plan...</p>
      </main>
    );
  }

  if (error && !plan) {
    return (
      <main className="mx-auto max-w-lg p-6">
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-amber-800">
          {error}
          {menu?.items.length === 0 && (
            <p className="mt-2 text-sm">
              No menu for today. Run the scraper first: <code className="rounded bg-amber-100 px-1">POST /api/scrape/run</code> (or use seed data).
            </p>
          )}
        </div>
        <Link href="/" className="mt-4 inline-block text-slate-600 underline">← Back to targets</Link>
        <button onClick={generate} disabled={generating} className="ml-4 rounded bg-slate-800 px-4 py-2 text-white disabled:opacity-50">
          {generating ? "Generating..." : "Generate plan"}
        </button>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Today’s plan</h1>
        <Link href="/" className="text-slate-600 underline">Edit targets</Link>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">{error}</div>
      )}

      {plan && (
        <>
          <div className="space-y-6">
            {(["breakfast", "lunch", "dinner"] as const).map((slot) => (
              <section key={slot} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="mb-2 flex items-center justify-between">
                  <h2 className="font-semibold capitalize text-slate-800">{slot}</h2>
                  <button
                    onClick={() => regenerateMeal(slot)}
                    disabled={generating}
                    className="text-sm text-slate-600 underline disabled:opacity-50"
                  >
                    Regenerate
                  </button>
                </div>
                <ul className="space-y-1 text-slate-700">
                  {plan[slot].items.map((it) => (
                    <li key={it.id}>{it.name} — Cal: {it.calories}, P: {it.protein}g, C: {it.carbs}g, F: {it.fat}g</li>
                  ))}
                </ul>
                <p className="mt-2 text-sm text-slate-500">
                  Subtotal: {plan[slot].calories} cal, {plan[slot].protein}g P, {plan[slot].carbs}g C, {plan[slot].fat}g F
                </p>
              </section>
            ))}
          </div>

          <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <h3 className="font-semibold text-slate-800">Daily totals</h3>
            <p className="text-slate-700">
              Calories: {plan.totals.calories} | Protein: {plan.totals.protein}g | Carbs: {plan.totals.carbs}g | Fat: {plan.totals.fat}g
            </p>
            <p className="mt-1 text-sm text-slate-500">
              Deltas vs target: Cal {plan.deltas.calories >= 0 ? "+" : ""}{plan.deltas.calories}, P {plan.deltas.protein >= 0 ? "+" : ""}{plan.deltas.protein}g, C {plan.deltas.carbs >= 0 ? "+" : ""}{plan.deltas.carbs}g, F {plan.deltas.fat >= 0 ? "+" : ""}{plan.deltas.fat}g
            </p>
            <button
              onClick={generate}
              disabled={generating}
              className="mt-3 rounded bg-slate-800 px-4 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
            >
              {generating ? "Generating..." : "Regenerate full plan"}
            </button>
          </div>
        </>
      )}
    </main>
  );
}
