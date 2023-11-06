from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    
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
    

    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}