import pytest
from jose import jwt
from fastapi.testclient import TestClient
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.config.config import settings
from app.schemas import user, token

from app.models import models
from app.schemas.token import Token


@pytest.fixture
def test_user():
    return {"username":"test1@example.com",
            "password":"Password1!"}

@pytest.fixture
def mock_db_session():
    # Mock the AsyncSession here
    pass
    
@pytest.mark.asyncio
async def test_valid_login(test_user, mock_db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/login", data=test_user)
    print(response.text)  # Add this line to debug
    assert response.status_code == 200
    assert "access_token" in response.json()