import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_flow(async_client: AsyncClient):
    # 1. Register a new user
    register_payload = {
        "email": "engineer@enterprise.io",
        "username": "lead_dev",
        "password": "SuperSecurePassword123!",
        "full_name": "Lead Cloud Engineer",
        "role": "operator",
    }
    reg_resp = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["username"] == "lead_dev"
    assert user_data["email"] == "engineer@enterprise.io"

    # 2. Login with valid credentials
    login_data = {"username": "lead_dev", "password": "SuperSecurePassword123!"}
    login_resp = await async_client.post("/api/v1/auth/login", data=login_data)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 3. Login with wrong password
    bad_login = {"username": "lead_dev", "password": "WrongPassword!"}
    bad_resp = await async_client.post("/api/v1/auth/login", data=bad_login)
    assert bad_resp.status_code == 401
