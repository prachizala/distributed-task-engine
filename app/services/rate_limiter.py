import time
from typing import Optional

import redis.asyncio as aioredis

from app.config import settings


class RedisRateLimiter:
    """
    Sliding window log rate limiter backed by Redis.
    Falls back to an in-memory dictionary when Redis is unavailable.
    """

    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self._redis_client: Optional[aioredis.Redis] = None
        self._memory_cache: dict[str, list[float]] = {}

    async def get_client(self) -> Optional[aioredis.Redis]:
        if self._redis_client is None:
            try:
                client = aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=1.0,
                    socket_timeout=1.0,
                )
                await client.ping()
                self._redis_client = client
            except Exception:
                self._redis_client = None
        return self._redis_client

    async def is_allowed(
        self,
        identifier: str,
        limit: int = settings.RATE_LIMIT_REQUESTS,
        window: int = settings.RATE_LIMIT_WINDOW_SECONDS,
    ) -> tuple[bool, int]:
        """
        Returns (is_allowed, remaining_quota)
        """
        now = time.time()
        client = await self.get_client()

        if client is not None:
            try:
                key = f"rate_limit:{identifier}"
                pipeline = client.pipeline()
                # Remove timestamps older than window
                pipeline.zremrangebyscore(key, 0, now - window)
                # Count remaining elements in window
                pipeline.zcard(key)
                # Add current request timestamp
                pipeline.zadd(key, {str(now): now})
                # Set TTL on key
                pipeline.expire(key, window + 1)
                results = await pipeline.execute()

                current_count = results[1]
                remaining = max(0, limit - (current_count + 1))
                return (current_count < limit), remaining
            except Exception:
                pass

        # In-memory fallback
        timestamps = self._memory_cache.setdefault(identifier, [])
        cutoff = now - window
        self._memory_cache[identifier] = [t for t in timestamps if t > cutoff]
        current_count = len(self._memory_cache[identifier])

        if current_count < limit:
            self._memory_cache[identifier].append(now)
            return True, limit - (current_count + 1)
        return False, 0


rate_limiter = RedisRateLimiter()
