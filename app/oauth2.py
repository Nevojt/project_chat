
from jose import JWTError, jwt
from datetime import datetime, timedelta

from sqlalchemy import select
from . import schemas, database, models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


async def create_access_token(data: dict):
    """
    Generate a JWT access token
    Args:
        data (dict): payload to include in the access token
    Returns:
        str: the access token
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    """
    Verify an access token and retrieve the user's ID.

    Args:
        token (str): The access token to verify.
        credentials_exception (HTTPException): The exception to raise if the credentials are invalid.

    Returns:
        TokenData: The user's ID.

    Raises:
        HTTPException: If the credentials are invalid.
    """

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        
        raise credentials_exception

    return token_data
    
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(database.get_async_session)):
    """
    Get the currently authenticated user.

    Args:
        token (str): The access token.
        db (AsyncSession): The database session.

    Returns:
        models.User: The currently authenticated user.

    Raises:
        HTTPException: If the credentials are invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = verify_access_token(token, credentials_exception)
    
    async with db.begin() as session:
        user = await db.execute(select(models.User).filter(models.User.id == token.id))
        user = user.scalar()
    
    return user


async def create_refresh_token(user_id: str):
    expire = datetime.utcnow() + timedelta(days=7)  # Наприклад, токен оновлення дійсний 7 днів
    to_encode = {"exp": expire, "user_id": user_id}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt