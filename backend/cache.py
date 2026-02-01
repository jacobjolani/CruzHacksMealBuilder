import json
import time
from typing import Any, Optional

import redis

from backend.config import settings


_redis: Optional[redis.Redis] = None


def get_redis() -> Optional[redis.Redis]:
    global _redis
    if _redis is not None:
        return _redis
    try:
        _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        # quick connectivity check
        _redis.ping()
        return _redis
    except Exception:
        _redis = None
        return None


def cache_get_json(key: str) -> Optional[Any]:
    r = get_redis()
    if r is None:
        return None
    raw = r.get(key)
    if raw is None:
        r.incr("cache:misses")
        return None
    r.incr("cache:hits")
    return json.loads(raw)


def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    r = get_redis()
    if r is None:
        return
    r.setex(key, ttl_seconds, json.dumps(value))


def cache_stats() -> dict[str, Any]:
    r = get_redis()
    if r is None:
        return {"enabled": False, "hits": 0, "misses": 0, "hit_rate": None, "timestamp": time.time()}

    hits = int(r.get("cache:hits") or 0)
    misses = int(r.get("cache:misses") or 0)
    total = hits + misses
    hit_rate = (hits / total) if total else None
    return {"enabled": True, "hits": hits, "misses": misses, "hit_rate": hit_rate, "timestamp": time.time()}

