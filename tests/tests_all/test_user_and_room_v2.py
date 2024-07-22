import json
import pytest
from httpx import AsyncClient
from jose import jwt
import asyncio


from app.config.config import settings
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import user, token
from .utils import random_email, random_lower_string

client = TestClient(app)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def async_session():
    from app.database import get_async_session  # Імпорт get_async_session тут
    async for session in get_async_session():
        yield session

@pytest.fixture
def test_user_create():
    return {"email": random_email(),
            "password": "password123"}

@pytest.mark.asyncio
async def test_create_user_v2(test_user_create, async_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_name = random_lower_string()
        email = test_user_create["email"]
        password = test_user_create["password"]

        response = await client.post(
            "/users/v2",
            data={
                "email": email,
                "user_name": user_name,
                "password": password
            },
            files={"file": (None, "", "application/octet-stream")}
        )

        assert response.status_code == 201
        new_user = user.UserOut(**response.json())
        assert new_user.user_name == user_name

@pytest.fixture
def test_login_user_fixture():
    return {"email": "test_user@test.testing",
            "password": "password123"}

@pytest.mark.asyncio
async def test_login_user_login(test_login_user_fixture, async_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.post(
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
async def test_verify_user(test_user_verify, async_session):
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

        user = next((u for u in users if u['email'] == test_user_verify['email']), None)
        assert user is not None
        token_verify = user['token_verify']

    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/success_registration",
                                    headers=headers,
                                    params={'token': token_verify},
                                    follow_redirects=False)

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
async def test_update_user(test_user_update_login, test_user_update, async_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_res = await client.post("/login", 
                                      data={"username": test_user_update_login['email'],
                                            "password": test_user_update_login['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']

    async with AsyncClient(app=app, base_url="http://test") as client:
        user_info_res = await client.get("/users/", 
                                         headers={"Authorization": f"Bearer {token}"})
        assert user_info_res.status_code == 200

    new_data = {
        "user_name": test_user_update["user_name"],
        "avatar": test_user_update["avatar"]
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(f"/users/",
                                    headers=headers,
                                    json=new_data,
                                    follow_redirects=False)

    assert response.status_code == 200
    assert response.json()['user_name'] == test_user_update["user_name"]

@pytest.fixture
def test_user_new_password():
    return {"email":"test_user@gmail.com",
            "password":"NewPassword"}

@pytest.fixture
def test_user_update_password():
    return {"email": "testuserupdatepassword@test.testing",
            "password": "NewPassword"}

@pytest.mark.asyncio
async def test_change_user_password(test_user_update_password, test_user_new_password, async_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
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

    async with AsyncClient(app=app, base_url="http://test") as client:
        res_password = await client.put("/manipulation/password",
                                        headers={"Authorization": f"Bearer {token}"},
                                        json=change_password)
        
        assert res_password.status_code == 200

@pytest.fixture
def test_user_delete_login():
    return {
        "email": "userdelete@delete.userdel",
        "user_name": "userdelete",
        "avatar": "userdelete",
        "password": "password123"
    }


@pytest.mark.asyncio
async def test_create_user_v2_del(test_user_delete_login, async_session):
    async with AsyncClient(app=app, base_url="http://test") as client:

        response = await client.post(
            "/users/test",
            json={
                "email": test_user_delete_login["email"],
                "user_name": test_user_delete_login["user_name"],
                "avatar": test_user_delete_login["avatar"],  # Додано поле avatar
                "password": test_user_delete_login["password"],
                "verified": True
            }
        )

        assert response.status_code == 201


@pytest.mark.asyncio
async def test_delete_user(test_user_delete_login, async_session):
    # Log in the user
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post(
            "/login",
            data={"username": test_user_delete_login['email'], "password": test_user_delete_login['password']}
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        token = login_data['access_token']

        # Delete the user
        delete_response = await client.request(
        "DELETE",
        "/users/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        content=json.dumps({"password": test_user_delete_login['password']})  # Передаємо пароль у форматі JSON
    )

        assert delete_response.status_code == 204


#  Block Rooms

@pytest.fixture
def test_user():
    return {"email":"utest_user_room@gmail.com",
            "password":"password123"}

@pytest.fixture
def test_room():
    return {"name_room": "Test Room Created",
            "image_room": "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/Content%20Home%20page/Desktop/Danger%20in%20nature.jpg",
            "secret_room": True}
    


    
@pytest.mark.asyncio
async def test_created_rooms(test_user, test_room, async_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']
        
        headers = {"Authorization": f"Bearer {token}"}
        
        
        
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/rooms/v2",
                            headers=headers, 
                            data={
                                "name_room": test_room['name_room'],
                                "image_room": test_room['image_room'],
                                "secret_room": test_room['secret_room']},
                            files={"file": (None, "", "application/octet-stream")})
        assert response.status_code == 201

    
@pytest.mark.asyncio
async def test_get_one_name(test_room, async_session):
    room = test_room['name_room']
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/rooms/{room}")
        assert response.status_code == 200
        assert response.json()['name_room'] == test_room['name_room']

@pytest.mark.asyncio
async def test_get_all_room(async_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/rooms/")
        assert response.status_code == 200


@pytest.fixture
def test_update_room():
    return {"name_room": "Test Room Update",
            "image_room": "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/Content%20Home%20page/Desktop/Winter%20fun.jp",
            "secret_room": True}
     
@pytest.mark.asyncio
async def test_update_rooms(test_user, test_room, test_update_room, async_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']
        
        headers = {"Authorization": f"Bearer {token}"}
        
    async with AsyncClient(app=app, base_url="http://test") as client:
        room = test_room['name_room']
        response = await client.get(f"rooms/{room}")
        assert response.status_code == 200
        room_data = response.json()
        id_room = room_data['id']

        
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(f"/rooms/{id_room}",
                            headers=headers, 
                            json=test_update_room,
                            follow_redirects=False)
        assert response.status_code == 200
        assert response.json()['name_room'] == test_update_room['name_room']



@pytest.mark.asyncio
async def test_delete_rooms(test_user, test_update_room, async_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']
        
        headers = {"Authorization": f"Bearer {token}"}
        
    async with AsyncClient(app=app, base_url="http://test") as client:
        room = test_update_room['name_room']
        response = await client.get(f"rooms/{room}")
        assert response.status_code == 200
        room_data = response.json()
        id_room = room_data['id']

        
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(f"/rooms/{id_room}",
                            headers=headers,
                            follow_redirects=False)
        assert response.status_code == 204