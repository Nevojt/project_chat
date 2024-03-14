import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status, HTTPException
from unittest.mock import MagicMock
from unittest.mock import AsyncMock
from app.routers.user.auth import login  # Import the login function from your app
from app.config import utils
from app.auth import oauth2


@pytest.mark.asyncio
async def test_login_success():
    # Arrange
    test_email = "test@example.com"
    test_password = "password"
    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.email = test_email
    fake_user.password = "hashed_password"

    user_credentials = OAuth2PasswordRequestForm(username=test_email, password=test_password)
    print(user_credentials)
    db_mock = AsyncMock(AsyncSession)
    db_mock.execute = AsyncMock(return_value=fake_user)

    # Mock verify and token creation functions
    utils.verify = MagicMock(return_value=True)
    oauth2.create_access_token = AsyncMock(return_value="access_token")
    oauth2.create_refresh_token = AsyncMock(return_value="refresh_token")

    # Act
    response = await login(user_credentials, db_mock)

    # Assert
    assert response["access_token"] == "access_token"
    assert response["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    # Arrange similar to the first test but mock utils.verify to return False
    test_email = "testinvalid@example.com"
    test_password = "passwordinvalid"
    db_mock = AsyncMock(AsyncSession)
    user_credentials = OAuth2PasswordRequestForm(username=test_email, password=test_password)

    # Act and Assert
    with pytest.raises(HTTPException) as exc_info:
        await login(user_credentials, db_mock)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED