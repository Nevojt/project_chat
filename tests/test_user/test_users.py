import pytest
from httpx import AsyncClient
from jose import jwt
import json

from app.config.config import settings
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import user, token



@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user():
    return {"email":"test_user@gmail.com",
            "password":"password123"}

@pytest.fixture
def test_user_update():
    return {"user_name": "User test Update",
            "avatar": "New avatar"}


def test_create_user(test_user, client):
    res = client.post(
        "/users/", json={"email": test_user["email"],
                         "password": test_user["password"],
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

def test_incorrect_error(client):
    res = client.post(
        "/login", data={"username": "email@gmail.com", "password": "password"})

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_update_user(test_user, test_user_update):
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Authenticate the user
        login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']
        
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Get user's information to find the user ID
        user_info_res = await client.get("/users/", headers={"Authorization": f"Bearer {token}"})
        assert user_info_res.status_code == 200


    # Step 2: Update the user
    new_data = {
        "user_name": test_user_update["user_name"],
        "avatar": test_user_update["avatar"]
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # # The 'put' request must also be inside the 'async with' block
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(f"/users/",
                                    headers=headers,
                                    json=new_data,
                                    follow_redirects=False
                                    )

    # Step 3: Assert the response
    assert response.status_code == 200
    assert response['user_name'] == new_data['user_name']


@pytest.mark.asyncio
async def test_delete_user(test_user):
    # Authenticate the user to get a token
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Authenticate the user
        login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']

        # Get user's information to find the user ID
        # user_info_res = await client.get("/users/", headers={"Authorization": f"Bearer {token}"})
        # assert user_info_res.status_code == 200
        # users_list = user_info_res.json()
        # user_id = users_list[0]['id']
        
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {"password": test_user["password"]}

        # Attempt to delete the user using the 'request' method directly
    async with AsyncClient(app=app, base_url="http://test") as client:
        delete_res = await client.delete(f"/users/",
                                         headers=headers,
                                         json=data,
                                         follow_redirects=False)

    assert delete_res.status_code == 204
