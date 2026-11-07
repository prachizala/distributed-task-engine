import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "Distributed Task" in data["title"]


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    assert data["components"]["database"] == "connected"
