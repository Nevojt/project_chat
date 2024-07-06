
import pytest
from fastapi.testclient import TestClient
from app.main import app
import asyncio
from httpx import AsyncClient

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
    await session.rollback()
    
@pytest.fixture
def test_user():
    return {"email":"utest_user_room@gmail.com",
            "password":"password123"}

@pytest.fixture
def test_room():
    return {"name_room": "Test Room Created",
            "image_room": "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/Content%20Home%20page/Desktop/Danger%20in%20nature.jpg",
            "secret_room": True}
    


    
# @pytest.mark.asyncio
# async def test_created_rooms(test_user, test_room, async_session):
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
#         assert login_res.status_code == 200
#         login_data = login_res.json()
#         token = login_data['access_token']
        
#         headers = {"Authorization": f"Bearer {token}"}
        
        
        
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         response = await client.post("/rooms/",
#                             headers=headers, 
#                             json=test_room,
#                             follow_redirects=False)
#         assert response.status_code == 201

    
# @pytest.mark.asyncio
# async def test_get_one_name(test_room, async_session):
#     room = test_room['name_room']
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         response = await client.get(f"/rooms/{room}")
#         assert response.status_code == 200
#         assert response.json()['name_room'] == test_room['name_room']
    


# @pytest.fixture
# def test_update_room():
#     return {"name_room": "Test Room Update",
#             "image_room": "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/Content%20Home%20page/Desktop/Winter%20fun.jp",
#             "secret_room": True}
     
# @pytest.mark.asyncio
# async def test_update_rooms(test_user, test_room, test_update_room, async_session):
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
#         assert login_res.status_code == 200
#         login_data = login_res.json()
#         token = login_data['access_token']
        
#         headers = {"Authorization": f"Bearer {token}"}
        
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         room = test_room['name_room']
#         response = await client.get(f"rooms/{room}")
#         assert response.status_code == 200
#         room_data = response.json()
#         id_room = room_data['id']

        
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         response = await client.put(f"/rooms/{id_room}",
#                             headers=headers, 
#                             json=test_update_room,
#                             follow_redirects=False)
#         assert response.status_code == 200
#         assert response.json()['name_room'] == test_update_room['name_room']



# @pytest.mark.asyncio
# async def test_delete_rooms(test_user, test_update_room, async_session):
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
#         assert login_res.status_code == 200
#         login_data = login_res.json()
#         token = login_data['access_token']
        
#         headers = {"Authorization": f"Bearer {token}"}
        
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         room = test_update_room['name_room']
#         response = await client.get(f"rooms/{room}")
#         assert response.status_code == 200
#         room_data = response.json()
#         id_room = room_data['id']

        
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         response = await client.delete(f"/rooms/{id_room}",
#                             headers=headers,
#                             follow_redirects=False)
#         assert response.status_code == 204
    



# # @pytest.mark.asyncio   
# # async def test_get_rooms_manager(test_user):
# #     async with AsyncClient(app=app, base_url="http://test") as client:
# #         login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
# #         assert login_res.status_code == 200
# #         login_data = login_res.json()
# #         token = login_data['access_token']
        
# #         headers = {"Authorization": f"Bearer {token}"}
        
# #     async with AsyncClient(app=app, base_url="http://test") as client:
# #         response = await client.get("/favorites/", headers=headers)
# #         assert response.status_code == 200
        
        
    

    