import pytest
from fastapi.testclient import TestClient
from app.main import app





@pytest.fixture
def client():
    return TestClient(app)
    

# @pytest.mark.asyncio
# async def test_created_user(client):
#     res = client.post("/users/", json={
#         "email": "test1@example.com",
#         "user_name": "TestUser",
#         "password": "Password1!",
#         "avatar": "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/content%20common%20chat/Avatar%20Mobile/Boy%2015%20mobile.png",
#         })
    
#     new_user = user.UserOut(**res.json())
#     assert new_user.user_name == "TestUser"
#     assert res.status_code == 201 # status code for successful