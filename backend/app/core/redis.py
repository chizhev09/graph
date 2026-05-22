from redis import asyncio as aioredis
from redis.exceptions import RedisError

from app.core.config import get_settings

_redis: aioredis.Redis | None = None
_redis_unavailable = False


async def get_redis() -> aioredis.Redis | None:
    global _redis, _redis_unavailable
    if _redis_unavailable:
        return None
    if _redis is None:
        settings = get_settings()
        client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        try:
            await client.ping()
            _redis = client
        except (RedisError, OSError):
            _redis_unavailable = True
            await client.aclose()
            return None
    return _redis


async def close_redis() -> None:
    global _redis, _redis_unavailable
    if _redis is not None:
        await _redis.aclose()
        _redis = None
    _redis_unavailable = False
