import type { Request, Response, NextFunction } from "express";

const SESSION_COOKIE = "sessionId";
const MAX_AGE_DAYS = 365;

export function sessionMiddleware(req: Request, res: Response, next: NextFunction) {
  let sessionId = req.cookies?.[SESSION_COOKIE];
  if (!sessionId) {
    sessionId = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 12)}`;
    res.cookie(SESSION_COOKIE, sessionId, { httpOnly: true, maxAge: MAX_AGE_DAYS * 24 * 60 * 60 * 1000, path: "/" });
  }
  (req as Request & { sessionId: string }).sessionId = sessionId;
  next();
}
