import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import user


@pytest.fixture
def client():
    return TestClient(app)
    

# @pytest.mark.asyncio
def test_update_user(client):
    res = client.post("/users/", json={
        "user_name": "TestUserUpdate",
        "avatar": "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/content%20common%20chat/Avatar%20Mobile/Boy%2015%20mobile.png",
        })
    
    new_user = user.UserUpdate(**res.json())
    assert new_user.user_name == "TestUserUpdate"
    assert res.status_code == 200 # status code for successful