
import logging
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import async_db

from ...config import utils
from ...auth import oauth2
from app.config.config import settings
from app.models import models
from app.schemas.token import Token

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

logging.basicConfig(filename='_log/authentication.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(async_db.get_async_session)):
        
    """
    OAuth2-compatible token login, get an access token for future requests.

    Args:
    user_credentials (OAuth2PasswordRequestForm): The OAuth2 password request form data.
    db (Session): Dependency that gets the database session.

    Returns:
    JSON object with the access token and the token type.

    Raises:
    HTTPException: 403 Forbidden error if the credentials are invalid.

    The function performs the following steps:
    - Extracts the username and password from the OAuth2PasswordRequestForm.
    - Verifies that a user with the provided email exists in the database.
    - Checks if the provided password is correct.
    - Generates an access token using the user's ID.
    - Returns the access token and the token type as a JSON object.
    """
    try:
        query = select(models.User).where(models.User.email == user_credentials.username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user or not utils.verify(user_credentials.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

        access_token = await oauth2.create_access_token(data={"user_id": user.id})
        
        refresh_token = await oauth2.create_refresh_token(user.id)
        user.refresh_token = refresh_token
        await db.commit()

        # Return the token
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}
        
    except HTTPException as ex_error:
        logger.error(f"Error processing Authentication {ex_error}", exc_info=True)
        # Re-raise HTTPExceptions without modification
        raise
    except Exception as e:
        # Log the exception or handle it as you see fit
        logger.error(f"An error occurred: Authentication {e}", exc_info=True)
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while processing the request.")

@router.post("/refresh")
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(async_db.get_async_session)):
    """
    Endpoint to refresh an access token using a refresh token.

    Args:
        refresh_token (str): The refresh token to use for refreshing the access token.
        db (AsyncSession): The database session to use for accessing the database.

    Returns:
        JSON: The new access token and its type.

    Raises:
        HTTPException: If the refresh token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        
        new_access_token = await oauth2.create_access_token({"user_id": user_id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise credentials_exception