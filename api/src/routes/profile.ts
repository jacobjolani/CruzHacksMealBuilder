import { Router } from "express";
import { prisma } from "../lib/prisma.js";

export const profileRouter = Router();

profileRouter.post("/api/profile", async (req, res) => {
  const sessionId = (req as unknown as { sessionId?: string }).sessionId ?? "";
  if (!sessionId) {
    return res.status(400).json({ error: "Missing sessionId; ensure session middleware runs" });
  }

  const { dailyCalories, dailyProtein, dailyCarbs, dailyFat, preferences } = req.body ?? {};
  const prefsJson = preferences != null ? JSON.stringify(preferences) : undefined;

  await prisma.userProfile.upsert({
    where: { sessionId },
    create: {
      sessionId,
      dailyCalories: dailyCalories != null ? Number(dailyCalories) : null,
      dailyProtein: dailyProtein != null ? Number(dailyProtein) : null,
      dailyCarbs: dailyCarbs != null ? Number(dailyCarbs) : null,
      dailyFat: dailyFat != null ? Number(dailyFat) : null,
      preferences: prefsJson,
    },
    update: {
      dailyCalories: dailyCalories != null ? Number(dailyCalories) : undefined,
      dailyProtein: dailyProtein != null ? Number(dailyProtein) : undefined,
      dailyCarbs: dailyCarbs != null ? Number(dailyCarbs) : undefined,
      dailyFat: dailyFat != null ? Number(dailyFat) : undefined,
      preferences: prefsJson ?? undefined,
    },
  });

  return res.json({ ok: true });
});

profileRouter.get("/api/profile", async (req, res) => {
  const sessionId = (req as unknown as { sessionId?: string }).sessionId ?? "";
  if (!sessionId) {
    return res.json({ profile: null });
  }

  const profile = await prisma.userProfile.findUnique({
    where: { sessionId },
  });

  if (!profile) return res.json({ profile: null });

  const preferences = profile.preferences ? JSON.parse(profile.preferences) : undefined;
  return res.json({
    profile: {
      dailyCalories: profile.dailyCalories,
      dailyProtein: profile.dailyProtein,
      dailyCarbs: profile.dailyCarbs,
      dailyFat: profile.dailyFat,
      preferences,
    },
  });
});
