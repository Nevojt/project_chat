import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.orm import Session
from app.schemas import room as room_schemas

from app.database.database import engine
from httpx import AsyncClient

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    db = Session(bind=engine)
    yield db
    db.close()
    
    
@pytest.fixture
def test_user():
    return {"email":"test_user_room@gmail.com",
            "password":"password123"}

@pytest.fixture
def test_room():
    return {"name_room": "Test Room Created",
            "image_room": "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/Content%20Home%20page/Desktop/Danger%20in%20nature.jpg",
            "secret_room": False}
    
@pytest.fixture
def test_update_room():
    return {"name_room": "Test Room Update",
            "image_room": "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/Content%20Home%20page/Desktop/Winter%20fun.jp",
            "secret_room": True}
    
def test_get_all_rooms(client):
    response = client.get("/rooms")
    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_created_rooms(test_user, test_room):
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']
        
        headers = {"Authorization": f"Bearer {token}"}
        
        
        
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/rooms/",
                            headers=headers, 
                            json=test_room,
                            follow_redirects=False)
        assert response.status_code == 201

    

def test_get_one_name(client, test_room):
    room = test_room['name_room']
    response = client.get(f"/rooms/{room}")
    assert response.status_code == 200
    assert response.json()['name_room'] == test_room['name_room']
    
    
@pytest.mark.asyncio
async def test_update_rooms(test_user,test_room, test_update_room):
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
async def test_get_rooms_manager(test_user):
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_res = await client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
        assert login_res.status_code == 200
        login_data = login_res.json()
        token = login_data['access_token']
        
        headers = {"Authorization": f"Bearer {token}"}
        
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/rooms/manager", headers=headers)
        assert response.status_code == 200
        
        
    

    