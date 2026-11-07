from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.config import settings
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Graceful shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
## ⚡ High-Throughput Distributed Task & Asynchronous Job Processing Engine

An enterprise backend architecture designed for background task offloading, distributed job execution, and production observability.

### Core Capabilities:
* **Asynchronous API Layer**: Non-blocking request ingestion powered by FastAPI & Uvicorn.
* **Distributed Task Queue**: Scalable background workers powered by Celery & Redis broker.
* **Persistent Job Storage**: Full task audit logging & execution tracking using Async SQLAlchemy 2.0.
* **Intelligent Rate Limiting**: Redis Sliding-Window / Token-Bucket request throttler.
* **Security & RBAC**: JWT Access token validation with role-based access control.
* **Containerized Orchestration**: Production-ready Docker Compose blueprint for PostgreSQL, Redis, Celery & API.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "title": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health_probe": f"{settings.API_V1_STR}/health",
    }
