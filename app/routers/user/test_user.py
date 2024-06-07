import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from app.main import app
from app.auth import oauth2


# client = TestClient(app)

# Мок для сесії бази даних
# @pytest.fixture
# def mock_db_session():
#     with patch('app.database.async_db.async_session_maker') as mock:
#         async_session_mock = AsyncMock()
#         mock.return_value.__aenter__.return_value = async_session_mock
#         yield async_session_mock

# @pytest.mark.asyncio
# async def test_created_user():
#     user_data = {
#         "email": "test@example.com",
#         "password": "testpassword",
#         "user_name": "TestUser",
#         "avatar": "avatar_url"
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         with patch('app.database.async_db.get_async_session', return_value=AsyncMock()) as mocked_session:
#             mocked_db = mocked_session.return_value.__aenter__.return_value
#             mocked_db.execute.return_value.scalar_one_or_none.return_value = None

#             with patch('app.mail.send_mail.send_registration_mail', new_callable=AsyncMock) as mocked_mail:
#                 with patch('app.config.utils.hash', side_effect=lambda x: f"hashed_{x}") as mocked_hash:
#                     with patch('app.config.utils.generate_unique_token', return_value='unique_token123') as mocked_token:
#                         response = await ac.post("/users/", json=user_data)
                    
#                     assert response.status_code == 201
#                     assert mocked_mail.called
#                     assert mocked_hash.called
#                     assert mocked_token.called


@pytest.mark.asyncio
async def test_login_simple_db_access():
    user_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        with patch('app.database.async_db.get_async_session', new_callable=AsyncMock) as mocked_session:
            mocked_db = mocked_session.return_value.__aenter__.return_value
            # Setup mock to return a user object, ensuring it's an awaited call in the actual application
            mocked_db.execute.return_value.scalar_one_or_none.return_value = AsyncMock(
                email="user@example.com", 
                password="hashed_password", 
                blocked=False
            )

            response = await ac.post("/login", data=user_data)

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    if response.status_code != 200:
        print("Response data:", response.json())