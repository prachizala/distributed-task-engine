from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, tasks

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health & Probes"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Security"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Distributed Task Management"])
