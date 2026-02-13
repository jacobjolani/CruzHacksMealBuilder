/**
 * In-memory cache: one plan per (date, sessionId, targetsSignature).
 * Different macro targets must not share a cache entry.
 */

type CacheKey = string;
const planCache = new Map<CacheKey, { plan: unknown; at: number }>();
const TTL_MS = 60 * 60 * 1000; // 1 hour

/** Stable string for targets so cache key changes when user changes macros */
export function targetsSignature(targets: Record<string, number | undefined>): string {
  const o: Record<string, number> = {};
  for (const [k, v] of Object.entries(targets)) {
    if (v != null && Number.isFinite(v)) o[k] = v;
  }
  return JSON.stringify(Object.keys(o).sort().map((k) => `${k}:${o[k]}`));
}

export function getCachedPlan(date: string, sessionId: string, targetsSig: string): unknown | null {
  const key: CacheKey = `plan:${date}:${sessionId}:${targetsSig}`;
  const entry = planCache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.at > TTL_MS) {
    planCache.delete(key);
    return null;
  }
  return entry.plan;
}

export function setCachedPlan(date: string, sessionId: string, targetsSig: string, plan: unknown): void {
  const key: CacheKey = `plan:${date}:${sessionId}:${targetsSig}`;
  planCache.set(key, { plan, at: Date.now() });
}

/** Invalidate all entries for this date+session (e.g. on regenerate) */
export function invalidatePlan(date: string, sessionId: string): void {
  const prefix = `plan:${date}:${sessionId}:`;
  for (const key of planCache.keys()) {
    if (key.startsWith(prefix)) planCache.delete(key);
  }
}
