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
def client():
    return TestClient(app)


@pytest.fixture
def test_user():
    return {"username":"test1@example.com",
            "password":"Password1!"}
    
@pytest.fixture
def test_user_invalid():
    return {"username":"invalid@example.com",
            "password":"Invalid!"}

    
@pytest.fixture
def mock_db_session():
    # Mock the AsyncSession here
    pass
    


# @pytest.mark.asyncio
# async def test_invalid_login(test_user_invalid, mock_db_session):
#     async with AsyncClient(app=app, base_url="http://testserver") as ac:
#         response = await ac.post("/login", data=test_user_invalid)
#     assert response.status_code == 401

@pytest.mark.asyncio
async def test_db_error(mock_db_session):
    # Mock a database error in mock_db_session
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/login", data={"username": "error@email.com", "password": "errorpassword"})
    assert response.status_code == 500