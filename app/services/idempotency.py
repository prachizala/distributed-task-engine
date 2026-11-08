import time
from typing import Optional

import redis.asyncio as aioredis

from app.config import settings


class IdempotencyService:
    """
    Manages client enqueue idempotency keys using Redis with in-memory fallback.
    Prevents duplicate task dispatches when clients retry HTTP requests.
    """

    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self._redis_client: Optional[aioredis.Redis] = None
        self._memory_cache: dict[str, tuple[str, float]] = {}

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

    async def get_existing_job_id(self, idempotency_key: str) -> Optional[str]:
        client = await self.get_client()
        redis_key = f"idempotency:{idempotency_key}"

        if client is not None:
            try:
                val = await client.get(redis_key)
                if val:
                    return str(val)
            except Exception:
                pass

        # In-memory check with TTL expiration
        now = time.time()
        if idempotency_key in self._memory_cache:
            job_id, expires_at = self._memory_cache[idempotency_key]
            if now < expires_at:
                return job_id
            del self._memory_cache[idempotency_key]

        return None

    async def record_job_id(
        self, idempotency_key: str, job_id: str, ttl_seconds: int = 600
    ) -> None:
        client = await self.get_client()
        redis_key = f"idempotency:{idempotency_key}"

        if client is not None:
            try:
                await client.set(redis_key, job_id, ex=ttl_seconds, nx=True)
                return
            except Exception:
                pass

        # In-memory store
        self._memory_cache[idempotency_key] = (job_id, time.time() + ttl_seconds)


idempotency_service = IdempotencyService()
