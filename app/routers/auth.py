
    

import logging
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import database, schemas, models, utils, oauth2

logging.basicConfig(filename='log/authentication.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(database.get_async_session)):
        
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

        # Return the token
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as ex_error:
        logger.error(f"Error processing Authentication {ex_error}", exc_info=True)
        # Re-raise HTTPExceptions without modification
        raise
    except Exception as e:
        # Log the exception or handle it as you see fit
        logger.error(f"An error occurred: Authentication {e}", exc_info=True)
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while processing the request.")
