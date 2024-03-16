import pytest
import asyncio
from unittest.mock import MagicMock
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import user
from tests.utils.utils import random_email, random_lower_string


mock_session=MagicMock()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db_session():
    # Mock the AsyncSession here
    yield mock_session
    
    
email = random_email()
password = random_lower_string()
@pytest.fixture
def test_user():
    return {"username":email,
            "password":password}


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
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/login", data=test_user)

    assert response.status_code == 200  # Assuming a successful login returns 200
    assert "access_token" in response.json()