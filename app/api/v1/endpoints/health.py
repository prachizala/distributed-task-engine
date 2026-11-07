from typing import Any, Dict

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.config import settings

router = APIRouter()


@router.get("", summary="System Health & Readiness Probe")
async def health_check(db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    # 1. Check Database connectivity
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unreachable ({e.__class__.__name__})"

    # 2. Check Redis connectivity
    redis_status = "connected"
    try:
        client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=1.0)
        await client.ping()
        await client.aclose()
    except Exception as e:
        redis_status = f"degraded ({e.__class__.__name__})"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "components": {
            "database": db_status,
            "redis": redis_status,
        },
    }
