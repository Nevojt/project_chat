import pytest
from jose import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app import schemas


client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.status_code == 200


# def test_created_user():
#     res = client.post("/users/", json={
#         "email": "test11@example.com",
#         "user_name": "TestUser",
#         "password": "password123",
#         "avatar": "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/content%20common%20chat/Avatar%20Mobile/Boy%2015%20mobile.png"
#         })
    
#     new_user = schemas.UserOut(**res.json())
#     assert new_user.user_name == "TestUser"
#     assert res.status_code == 201 # status code for successful
    
    
# def test_login_user(test_user, client):
#     res = client.post(
#         "/login", data={"username": test_user['email'], "password": test_user['password']})
#     login_res = schemas.Token(**res.json())
#     payload = jwt.decode(login_res.access_token,
#                          settings.secret_key, algorithms=[settings.algorithm])
#     id = payload.get("user_id")
#     assert id == test_user['id']
#     assert login_res.token_type == "bearer"
#     assert res.status_code == 200