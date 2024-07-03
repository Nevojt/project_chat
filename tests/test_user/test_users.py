import pytest
from httpx import AsyncClient
from jose import jwt
import json

from app.config.config import settings
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import user, token
from .utils import random_email, random_lower_string

client = TestClient(app)




@pytest.fixture
def test_user_create():
    return {"email": random_email(),
            "password": "password123"}

def test_create_user_v2(test_user_create):
    user_name = random_lower_string()
    email = test_user_create["email"]
    password = test_user_create["password"]

    response = client.post(
        "/users/v2",
        data={
            "email": email,
            "user_name": user_name,
            "password": password
        },
        files={"file": (None, "", "application/octet-stream")}  # Empty file field
    )

    assert response.status_code == 201
    new_user = user.UserOut(**response.json())
    assert new_user.user_name == user_name




@pytest.fixture
def test_login_user_fixture():
    return {"email": "test_user@test.testing",
            "password": "password123"}
      
def test_login_user_login(test_login_user_fixture):

    res = client.post(
        "/login", data={"username": test_login_user_fixture['email'], "password": test_login_user_fixture['password']}
    )
    
    assert res.status_code == 200
    login_res = token.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])

    assert login_res.token_type == "bearer"
    
  

@pytest.fixture
def test_user_verify():
    return {"email": "testuserverify@test.testing",
            "password": "password123"}

@pytest.mark.asyncio
async def test_verify_user(test_user_verify):
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Authenticate the user
        login_res = await client.post("/login", 
                                      data={"username": test_user_verify['email'],
                                            "password": test_user_verify['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Get user's information to find the user ID
        user_info_res = await client.get("/users/", 
                                         headers={"Authorization": f"Bearer {token}"})
        assert user_info_res.status_code == 200
        users = user_info_res.json()

        # Find the specific user
        user = next((u for u in users if u['email'] == test_user_verify['email']), None)
        assert user is not None
        token_verify = user['token_verify']

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # # The 'put' request must also be inside the 'async with' block
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/success_registration",
                                    headers=headers,
                                    params={'token': token_verify},
                                    follow_redirects=False
                                    )

    # Step 3: Assert the response
    assert response.status_code == 200
  
  
  
@pytest.fixture
def test_user_update():
    return {"user_name": "User test Update",
            "avatar": "New avatar"}
    
@pytest.fixture
def test_user_update_login():
    return {"email": "testuserverifyupdate@test.testing",
            "password": "password123"}
    
@pytest.mark.asyncio
async def test_update_user(test_user_update_login, test_user_update):
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Authenticate the user
        login_res = await client.post("/login", 
                                      data={"username": test_user_update_login['email'],
                                            "password": test_user_update_login['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']
        
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Get user's information to find the user ID
        user_info_res = await client.get("/users/", 
                                         headers={"Authorization": f"Bearer {token}"})
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
    assert response.json()['user_name'] == test_user_update["user_name"]



    
@pytest.fixture
def test_user_new_password():
    return {"email":"testuserupdatepassword@test.testing",
            "password":"NewPassword"}
    
@pytest.fixture
def test_user_update_password():
    return {"email": "testuserupdatepassword@test.testing",
            "password": "NewPassword"}

@pytest.mark.asyncio
async def test_change_user_password(test_user_update_password, test_user_new_password):
    # Authenticate the user to get a token
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Authenticate the user
        login_res = await client.post("/login",
                                      data={"username": test_user_update_password['email'],
                                            "password": test_user_update_password['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']

    headers = {
        "Authorization": f"Bearer {token}",
    }
    change_password = {
        "old_password": test_user_update_password['password'],
        "new_password": test_user_new_password['password']
    }

    # Attempt to change the user's password using the 'put' method with JSON body
    async with AsyncClient(app=app, base_url="http://test") as client:
        res_password = await client.put("/manipulation/password",
                                        headers={"Authorization": f"Bearer {token}"},
                                        json=change_password)
        
        
        assert res_password.status_code == 200


# @pytest.fixture
# def test_user_delete():
#     return {"email": "deleteuser@test.testing",
#             "password": "password123"
#             }

# @pytest.mark.asyncio
# async def test_delete_user(test_user_delete):
#     # Authenticate the user to get a token
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         # Authenticate the user
#         login_res = await client.post("/login", data={"username": test_user_delete['email'],
#                                                       "password": test_user_delete['password']})
#         assert login_res.status_code == 200
#         login_data = login_res.json()
#         token = login_data['access_token']
    
#     headers = {
#         "Authorization": f"Bearer {token}",
#     }
#     data = {
#         "password": test_user_new_password['password']
#     }

#     # Attempt to delete the user using the 'request' method with JSON body
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         delete_res = await client.request("DELETE", "/users/", 
#                                           headers=headers, json=data)

#     assert delete_res.status_code == 204

# @pytest.fixture
# def test_user_create_after_delete():
#     return {"email": "deleteuser@test.testing",
#             "password": "password123",
#             "user_name": "Test User Delete"}

# def test_create_user_v2_after_delete(test_user_create_after_delete):
#     user_name = test_user_create_after_delete["user_name"]
#     email = test_user_create_after_delete["email"]
#     password = test_user_create_after_delete["password"]

#     response = client.post(
#         "/users/v2",
#         data={
#             "email": email,
#             "user_name": user_name,
#             "password": password
#         },
#         files={"file": (None, "", "application/octet-stream")}  # Empty file field
#     )

#     assert response.status_code == 201
#     new_user = user.UserOut(**response.json())
#     assert new_user.user_name == user_name

