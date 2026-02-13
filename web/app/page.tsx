"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:4000";

type Profile = {
  dailyCalories?: number;
  dailyProtein?: number;
  dailyCarbs?: number;
  dailyFat?: number;
  preferences?: Record<string, unknown>;
};

export default function Home() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    dailyCalories: "",
    dailyProtein: "",
    dailyCarbs: "",
    dailyFat: "",
  });

  useEffect(() => {
    fetch(`${API}/api/profile`, { credentials: "include" })
      .then((r) => r.json())
      .then((d) => {
        if (d.profile) {
          setProfile(d.profile);
          setForm({
            dailyCalories: d.profile.dailyCalories ?? "",
            dailyProtein: d.profile.dailyProtein ?? "",
            dailyCarbs: d.profile.dailyCarbs ?? "",
            dailyFat: d.profile.dailyFat ?? "",
          });
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await fetch(`${API}/api/profile`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dailyCalories: form.dailyCalories ? Number(form.dailyCalories) : undefined,
          dailyProtein: form.dailyProtein ? Number(form.dailyProtein) : undefined,
          dailyCarbs: form.dailyCarbs ? Number(form.dailyCarbs) : undefined,
          dailyFat: form.dailyFat ? Number(form.dailyFat) : undefined,
        }),
      });
      setProfile({
        dailyCalories: form.dailyCalories ? Number(form.dailyCalories) : undefined,
        dailyProtein: form.dailyProtein ? Number(form.dailyProtein) : undefined,
        dailyCarbs: form.dailyCarbs ? Number(form.dailyCarbs) : undefined,
        dailyFat: form.dailyFat ? Number(form.dailyFat) : undefined,
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <p className="text-slate-500">Loading...</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-lg p-6">
      <h1 className="mb-2 text-2xl font-bold text-slate-800">Meal Planner</h1>
      <p className="mb-6 text-slate-600">
        Set your daily macro targets. We’ll build three meals (breakfast, lunch, dinner) from the UC Berkeley dining menu.
      </p>

      <form onSubmit={handleSave} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <label className="block text-sm font-medium text-slate-700">Calories</label>
          <input
            type="number"
            min="0"
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            value={form.dailyCalories}
            onChange={(e) => setForm((f) => ({ ...f, dailyCalories: e.target.value }))}
            placeholder="e.g. 2000"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Protein (g)</label>
          <input
            type="number"
            min="0"
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            value={form.dailyProtein}
            onChange={(e) => setForm((f) => ({ ...f, dailyProtein: e.target.value }))}
            placeholder="e.g. 150"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Carbs (g)</label>
          <input
            type="number"
            min="0"
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            value={form.dailyCarbs}
            onChange={(e) => setForm((f) => ({ ...f, dailyCarbs: e.target.value }))}
            placeholder="e.g. 200"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Fat (g)</label>
          <input
            type="number"
            min="0"
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            value={form.dailyFat}
            onChange={(e) => setForm((f) => ({ ...f, dailyFat: e.target.value }))}
            placeholder="e.g. 65"
          />
        </div>
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-slate-800 px-4 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save targets"}
          </button>
          <Link
            href="/plan"
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-700 hover:bg-slate-50"
          >
            Go to plan →
          </Link>
        </div>
      </form>

      {profile && (profile.dailyProtein != null || profile.dailyCalories != null) && (
        <p className="mt-4 text-sm text-slate-500">Targets saved. Go to Plan to generate today’s meals.</p>
      )}
    </main>
  );
}
