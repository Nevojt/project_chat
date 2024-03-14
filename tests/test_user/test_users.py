import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import user
from tests.utils.utils import random_email, random_lower_string


@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db_session():
    # Mock the AsyncSession here
    pass

@pytest.fixture
def test_user():
    return {"username":"test1@example.com",
            "password":"Password1!"}


@pytest.mark.asyncio
async def test_created_user(test_user, mock_db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        res = await ac.post("/users/", json={
            "email": test_user["username"],
            "user_name": "TestUser",
            "password": test_user["password"],
            "avatar": "avatar",
        })

    new_user = user.UserOut(**res.json())
    assert new_user.user_name == "TestUser"
    assert res.status_code == 201



@pytest.mark.asyncio
async def test_valid_login(test_user, mock_db_session):
    await asyncio.sleep(1)
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/login", data=test_user)
    print(response.text)  # Add this line to debug
    assert response.status_code == 200
    assert "access_token" in response.json()
