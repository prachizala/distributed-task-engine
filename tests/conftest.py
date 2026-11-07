import unittest.mock as mock
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db_session
from app.database import Base
from app.main import app
from app.workers.celery_app import celery_app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def mock_celery_send_task(monkeypatch):
    mock_async_result = mock.MagicMock()
    mock_async_result.id = "mock_celery_task_12345"
    monkeypatch.setattr(celery_app, "send_task", lambda *args, **kwargs: mock_async_result)


async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db_session] = override_get_db_session


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
