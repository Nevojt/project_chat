from fastapi import Response, status, HTTPException, Depends, APIRouter, Body
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_async_session
from ..database import get_db
from .. import models, schemas, utils, oauth2, send_mail
from typing import List

router = APIRouter(
    prefix="/users",
    tags=['Users'],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def created_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_async_session)):
    """
    Creates a new user in the database with the provided user details. It also checks for email uniqueness and hashes the password.

    Args:
        user (schemas.UserCreate): The user details for creating a new user.
        db (AsyncSession, optional): Asynchronous Database session dependency. Defaults to Depends(get_async_session).

    Raises:
        HTTPException: Raises a 424 error if a user with the given email already exists.

    Returns:
        models.User: The newly created user, along with their information, after being added to the database.
    """
    
    # Check if a user with the given email already exists
    query = select(models.User).where(models.User.email == user.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"User {existing_user.email} already exists")
    
    # Hash the user's password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    verification_token = utils.generate_unique_token(user.email)
    
    # Create a new user and add it to the database
    new_user = models.User(**user.model_dump(),
                           token_verify=verification_token)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create a User_Status entry for the new user
    post = models.User_Status(user_id=new_user.id, user_name=new_user.user_name, name_room="Hell")
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    registration_link = f"http://cool-chat.club/success_registration?token={new_user.token_verify}"
    await send_mail.send_registration_mail("Thank you for registration!", new_user.email,
                                           {
                                            "title": "Registration",
                                            "name": user.user_name,
                                            "registration_link": registration_link
                                            })
    
    return new_user




@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: int, 
    password: str = Body(...),  # Вимагайте пароль у тілі запиту
    db: AsyncSession = Depends(get_async_session), 
    current_user: int = Depends(oauth2.get_current_user)
):
    """
    Asynchronously deletes a user from the database.

    This endpoint allows a user to delete their own profile by providing their user ID and password. It performs several checks to ensure that the user is allowed to delete the profile, such as verifying the user's identity, checking the existence of the user, and ensuring the user is verified and authorized to perform the deletion.

    Parameters:
    - id (int): The unique identifier of the user to be deleted.
    - password (str): The password of the user to authenticate the deletion request.
    - db (AsyncSession): The database session used to perform database operations.
    - current_user (int): The user ID obtained from the current user session, used to ensure a user can only delete their own profile.

    Raises:
    - HTTPException: If the current user is not the user being deleted, if the user does not exist, if the user is not verified, or if the provided password is incorrect.

    Returns:
    - Response: An empty response with a 204 No Content status, indicating successful deletion.
    """
    
    
    # Переконайтесь, що користувач видаляє лише свій профіль
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not permitted to delete other users' profiles."
        )
    
    # Знайдіть користувача
    query = select(models.User).where(models.User.id == id)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    # Якщо користувач не існує, підніміть помилку 404
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with ID {id} does not exist.")
    # Перевірте, чи користувач верифікований
    if not existing_user.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only verified users can delete their profiles."
        )
    
    # Перевірте пароль
    if not utils.verify(password, existing_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )
    
    # Видаліть користувача
    await db.delete(existing_user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


     
        
    


@router.get('/{email}', response_model=schemas.UserInfo)
def get_user_mail(email: str, db: Session = Depends(get_db)):
    
    # Query the database for a user with the given email
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # If the user is not found, raise an HTTP 404 error
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email {email} not found")
        
    return user


@router.get("/", response_model=List[schemas.UserInfo])
async def get_email(db: Session = Depends(get_db)):
    # Query the database for all users
    posts = db.query(models.User).all()
    return posts