
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from typing import List
from ...database.database import get_db
from app.models import models
from app.schemas import user


router = APIRouter(
    prefix="/search",
    tags=['Search'],
)

@router.get('/user/{substring}', response_model=List[user.UserInfo])
def get_user_mail(substring: str, db: Session = Depends(get_db)):
    """
    Get a user by their email.

    Parameters:
    email (str): The email of the user to retrieve.
    db (Session): The database session to use.

    Returns:
    schemas.UserInfo: The user information, if found.

    Raises:
    HTTPException: If the user is not found.
    """
    
    pattern = f"{substring.lower()}%"  # Matches any username starting with 'substring'
    # Query the database for a user with the given username
    user = db.query(models.User).filter(func.lower(models.User.user_name).like(pattern)).all()
    # If the user is not found, raise an HTTP 404 error
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {pattern} not found")
        
    return user