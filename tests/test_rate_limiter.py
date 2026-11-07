import pytest

from app.services.rate_limiter import RedisRateLimiter


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_allows_and_blocks():
    # Force in-memory fallback by using an unreachable URL
    limiter = RedisRateLimiter(redis_url="redis://nonexistent:9999/0")

    identifier = "test_client_ip"
    limit = 3
    window = 10

    # 1. Allowed requests
    allowed, remaining = await limiter.is_allowed(identifier, limit=limit, window=window)
    assert allowed is True
    assert remaining == 2

    allowed, remaining = await limiter.is_allowed(identifier, limit=limit, window=window)
    assert allowed is True
    assert remaining == 1

    allowed, remaining = await limiter.is_allowed(identifier, limit=limit, window=window)
    assert allowed is True
    assert remaining == 0

    # 4th request should be blocked
    allowed, remaining = await limiter.is_allowed(identifier, limit=limit, window=window)
    assert allowed is False
    assert remaining == 0
