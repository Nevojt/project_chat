import pytest
import asyncio
from jose import jwt
from app.config.config import settings
from unittest.mock import MagicMock
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import user, token
from tests.utils.utils import random_email, random_lower_string


# mock_session=MagicMock()

@pytest.fixture
def client():
    return TestClient(app)

# @pytest.fixture
# def mock_db_session():
#     # Mock the AsyncSession here
#     yield mock_session
    
    
# email = random_email()
# password = random_lower_string()
@pytest.fixture
def test_user():
    return {"email":"hello123@gmail.com",
            "password":"password123"}


# @pytest.mark.asyncio
# async def test_created_user(test_user, mock_db_session):
#     async with AsyncClient(app=app, base_url="http://testserver") as ac:
#         res = await ac.post("/users/", json={
#             "email": test_user["username"],
#             "user_name": "TestUser",
#             "password": test_user["password"],
#             "avatar": "avatar",
#         })

#     new_user = user.UserOut(**res.json())
#     assert new_user.user_name == "TestUser"
#     assert res.status_code == 201



# @pytest.mark.asyncio
# async def test_valid_login(test_user, mock_db_session):
#     async with AsyncClient(app=app, base_url="http://testserver") as ac:
#         response = await ac.post("/login", data=test_user)

#     assert response.status_code == 200  # Assuming a successful login returns 200
#     assert "access_token" in response.json()




def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "hello123@gmail.com",
                         "password": "password123",
                         "user_name": "TestUser",
                         "avatar": "avatar"})

    new_user = user.UserOut(**res.json())
    assert new_user.user_name == "TestUser"
    assert res.status_code == 201
    
def test_login_user(test_user, client):
    res = client.post(
        "/login", data={"username": test_user['email'],
                        "password": test_user['password']})
    
    login_res = token.Token(**res.json())
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key,
                         algorithms=[settings.algorithm])

    assert login_res.token_type == "bearer"
    assert res.status_code == 200
    
@pytest.mark.parametrize("email, password, status_code", [
    (None, 'password123', 422),
    ('sanjeev@gmail.com', None, 422)
])
    
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post(
        "/login", data={"username": email, "password": password})

    assert res.status_code == status_code
    # assert res.json().get('detail') == 'Invalid Credentials'