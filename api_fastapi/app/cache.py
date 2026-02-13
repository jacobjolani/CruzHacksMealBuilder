"""
Redis cache layer with real hit/miss counters and logging.
Used for: menu fetch, meal plan generation.
"""
import json
import logging
from typing import Any, Optional

import redis

from app.config import settings

logger = logging.getLogger(__name__)

_redis: Optional[redis.Redis] = None

# Keys for metrics (counters)
CACHE_HITS = "cache:hits"
CACHE_MISSES = "cache:misses"


def get_redis() -> Optional[redis.Redis]:
    global _redis
    if _redis is not None:
        return _redis
    try:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
        _redis.ping()
        return _redis
    except Exception as e:
        logger.warning("Redis unavailable: %s", e)
        _redis = None
        return None


def cache_get(key: str) -> Optional[str]:
    r = get_redis()
    if r is None:
        return None
    val = r.get(key)
    if val is None:
        r.incr(CACHE_MISSES)
        logger.info("cache miss key=%s hits=%s misses=%s", key, r.get(CACHE_HITS) or 0, r.get(CACHE_MISSES) or 0)
        return None
    r.incr(CACHE_HITS)
    logger.info("cache hit key=%s hits=%s misses=%s", key, r.get(CACHE_HITS) or 0, r.get(CACHE_MISSES) or 0)
    return val


def cache_set(key: str, value: str, ttl_seconds: int) -> None:
    r = get_redis()
    if r is None:
        return
    r.setex(key, ttl_seconds, value)


def cache_get_json(key: str) -> Optional[Any]:
    raw = cache_get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    cache_set(key, json.dumps(value, default=str), ttl_seconds)


def cache_stats() -> dict[str, Any]:
    r = get_redis()
    if r is None:
        return {"enabled": False, "hits": 0, "misses": 0, "hit_rate": None}
    hits = int(r.get(CACHE_HITS) or 0)
    misses = int(r.get(CACHE_MISSES) or 0)
    total = hits + misses
    hit_rate = (hits / total) if total else None
    return {"enabled": True, "hits": hits, "misses": misses, "hit_rate": hit_rate}
