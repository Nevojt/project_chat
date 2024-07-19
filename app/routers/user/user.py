from datetime import datetime
from typing import List
from fastapi import Form, Response, status, HTTPException, Depends, APIRouter, UploadFile, File

import pytz
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mail import send_mail

from ...config import utils
from app.config.config import settings

from .hello import say_hello_system, system_notification_change_owner
from .created_image import generate_image_with_letter
from ...auth import oauth2
from ...database.async_db import get_async_session
from ...database.database import get_db
from app.models import user_model, room_model
from app.schemas import user






router = APIRouter(
    prefix="/users",
    tags=['Users'],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=user.UserOut)
async def created_user(user: user.UserCreate, db: AsyncSession = Depends(get_async_session)):
    """
    This function creates a new user in the database.

    Args:
        user (schemas.UserCreate): The user data to create.
        db (AsyncSession): The database session to use.

    Returns:
        schemas.UserOut: The newly created user.

    Raises:
        HTTPException: If a user with the given email already exists.
    """
    
    # Check if a user with the given email already exists
    query = select(user_model.User).where(user_model.User.email == user.email)
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
    new_user = user_model.User(**user.model_dump(),
                           token_verify=verification_token)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create a User_Status entry for the new user
    post = user_model.User_Status(user_id=new_user.id, user_name=new_user.user_name, name_room="Hell", room_id=1)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    registration_link = f"http://{settings.url_address_dns}/api/success_registration?token={new_user.token_verify}"
    await send_mail.send_registration_mail("Thank you for registration!", new_user.email,
                                           {
                                            "title": "Registration",
                                            "name": user.user_name,
                                            "registration_link": registration_link
                                            })
    await say_hello_system(new_user.id)
    
    return new_user


@router.post("/v2", status_code=status.HTTP_201_CREATED, response_model=user.UserOut)
async def created_user_v2(email: str = Form(...),
                          user_name: str = Form(...),
                          password: str = Form(...),
                          file: UploadFile = File(None),
                          db: AsyncSession = Depends(get_async_session)):
    """
    This function creates a new user in the database.

    Args:
        email (str): The email of the user.
        user_name (str): The user name of the user.
        password (str): The password of the user.
        file (UploadFile): The avatar file of the user.
        bucket_name (str): The name of the Backblaze B2 bucket to upload the file to.
        db (AsyncSession): The database session to use.

    Returns:
        schemas.UserOut: The newly created user.

    Raises:
        HTTPException: If a user with the given email already exists.
    """
    
    company = 1
    
    user_data = user.UserCreateV2(email=email, user_name=user_name, password=password)

# Check if a user with the given email already exists
    email_query = select(user_model.User).where(user_model.User.email == user_data.email)
    email_result = await db.execute(email_query)
    existing_email_user = email_result.scalar_one_or_none()

    if existing_email_user:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"User with email {existing_email_user.email} already exists")
    
    # Check if a user with the given user_name already exists
    username_query = select(user_model.User).where(user_model.User.user_name == user_data.user_name)
    username_result = await db.execute(username_query)
    existing_username_user = username_result.scalar_one_or_none()

    if existing_username_user:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"User with user_name {existing_username_user.user_name} already exists")
    
    # Hash the user's password
    hashed_password = utils.hash(user_data.password)
    user_data.password = hashed_password
    
    verification_token = utils.generate_unique_token(user_data.email)
    
    if file is None:
        generate_image_with_letter(user_name)
        avatar = await utils.upload_to_backblaze(settings.rout_image, settings.bucket_name_user_avatar)
    else:
        avatar = await utils.upload_to_backblaze(file, settings.bucket_name_user_avatar)
        
    # Create a new user and add it to the database
    new_user = user_model.User(**user_data.model_dump(),
                           avatar=avatar,
                           company_id=company, # Default company id
                           token_verify=verification_token)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create a User_Status entry for the new user
    post = user_model.User_Status(user_id=new_user.id, user_name=new_user.user_name, name_room="Hell", room_id=1)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    registration_link = f"http://{settings.url_address_dns}/api/success_registration?token={new_user.token_verify}"
    await send_mail.send_registration_mail("Thank you for registration!", new_user.email,
                                           {
                                            "title": "Registration",
                                            "name": user_data.user_name,
                                            "registration_link": registration_link
                                            })
    await say_hello_system(new_user.id)
    
    return new_user








@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    password: user.UserDelete,
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
    
    query = select(user_model.User).where(user_model.User.id == current_user.id)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    # If the user does not exist, raise a 404 error
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with ID  does not exist.")
    # Check if the user is verified
    if not existing_user.verified or existing_user.blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only verified users can delete their profiles or user in blocked."
        )
    
    if not utils.verify(password.password, existing_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )
        
    query_room = select(room_model.Rooms).where(room_model.Rooms.owner == current_user.id)
    result_room = await db.execute(query_room)
    rooms_to_update = result_room.scalars().all()
    
    for room in rooms_to_update:
        query_moderators = select(room_model.RoleInRoom).where(room_model.RoleInRoom.room_id == room.id, room_model.RoleInRoom.role == 'moderator')
        result_moderators = await db.execute(query_moderators)
        moderator = result_moderators.scalars().first()
        
        message = f"Room {room.name_room} is now owned by YOU"
        if moderator:
            room.owner = moderator.user_id
            moderator.role = 'owner'
            await system_notification_change_owner(moderator.user_id, message)
        else:
            room.owner = 0
        room.delete_at = datetime.now(pytz.utc)
        
    await db.commit()

    
    # delete user
    await db.delete(existing_user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


     
        
@router.put('/', response_model=user.UserInfo)
async def update_user(update: user.UserUpdate, 
                      db: Session = Depends(get_db), 
                      current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Update a user's information.

    Args:
        update (schemas.UserUpdate): The updated user information.
        db (Session): The database session to use.
        current_user (user_model.User): The currently authenticated user.

    Returns:
        schemas.UserInfo: The updated user information.

    Raises:
        HTTPException: If the user does not exist or if the user is not authorized to update the specified user.
    """
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not permitted to update other users' profiles."
        )
        
    if not current_user.verified or current_user.blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not verification or blocked."
        )
        
    user_query = db.query(user_model.User).filter(user_model.User.id == current_user.id)
    user = user_query.first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID: {current_user.id} not found"
        )
    
    user_status_query = db.query(user_model.User_Status).filter(user_model.User_Status.user_id == current_user.id)
    user_status = user_status_query.first()
    
    if user_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User status for ID: {current_user.id} not found"
        )
    
    # Assuming model_dump() returns a dictionary of attributes to update
    update_data = update.model_dump()

    user_query.update(update_data, synchronize_session=False)
    user_status_query.update({"user_name": update.user_name}, synchronize_session="fetch")
    
    db.commit()

    # Re-fetch or update the user object to reflect the changes
    updated_user = user_query.first()
    return updated_user
    
    
@router.put('/v2/avatar')
async def update_user_v2(file: UploadFile = File(...), 
                        db: Session = Depends(get_db), 
                        current_user: user_model.User = Depends(oauth2.get_current_user)):

        
    if not current_user.verified or current_user.blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not verification or blocked."
        )
        
    user_query = db.query(user_model.User).filter(user_model.User.id == current_user.id)
    user_data = user_query.first()
    
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID: {current_user.id} not found"
        )
    
    user_status_query = db.query(user_model.User_Status).filter(user_model.User_Status.user_id == current_user.id)
    user_status = user_status_query.first()
    
    if user_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User status for ID: {current_user.id} not found"
        )
    avatar = await utils.upload_to_backblaze(file)
    
    update = user.UserUpdateAvatar(avatar=avatar)
    update_data = update.model_dump()

    user_query.update(update_data, synchronize_session=False)
    db.commit()

 
    return "updated avatar"

@router.put('/v2/username')
async def update_user_v2(user_name: str = Form(...),
                        db: Session = Depends(get_db), 
                        current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Update a user's username.

    This function updates the username of the currently authenticated user in the database.
    It checks if the user is verified and not blocked before performing the update.
    If the user is not verified or blocked, it raises an HTTPException with a 403 status code.
    If the user is not found in the database, it raises an HTTPException with a 404 status code.

    Parameters:
    - user_name (str): The new username to be updated. This parameter is obtained from the request form.
    - db (Session): The database session to use for querying and updating the user's information.
    - current_user (user_model.User): The currently authenticated user. This parameter is obtained from the dependency injection.

    Returns:
    - str: A string indicating that the username has been updated.

    Raises:
    - HTTPException: If the user is not verified or blocked, or if the user is not found in the database.
    """
        
    if not current_user.verified or current_user.blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not verification or blocked."
        )
        
    user_query = db.query(user_model.User).filter(user_model.User.id == current_user.id)
    user_data = user_query.first()
    
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID: {current_user.id} not found"
        )
    
    user_status_query = db.query(user_model.User_Status).filter(user_model.User_Status.user_id == current_user.id)
    user_status = user_status_query.first()
    
    if user_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User status for ID: {current_user.id} not found"
        )
    
    update = user.UserUpdateUsername(user_name=user_name)
    update_data = update.model_dump()

    user_query.update(update_data, synchronize_session=False)
    user_status_query.update({"user_name": update.user_name}, synchronize_session="fetch")
    db.commit()

    # Re-fetch or update the user object to reflect the changes
    updated_user = user_query.first()
    return "updated username"


@router.get('/{email}', response_model=user.UserInfo)
def get_user_mail(email: str, db: Session = Depends(get_db)):
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
    
    # Query the database for a user with the given email
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    
    # If the user is not found, raise an HTTP 404 error
    if not user:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail=f"User with email {email} not found")
        
    return user

@router.get('/audit/{user_name}', response_model=user.UserInfo)
def get_user_name(user_name: str, db: Session = Depends(get_db)):
    """
    Get a user by their use_name.

    Parameters:
    user_name (str): The user_name of the user to retrieve.
    db (Session): The database session to use.

    Returns:
    schemas.UserInfo: The user information, if found.

    Raises:
    HTTPException: If the user is not found.
    """
    
    # Query the database for a user with the given email
    user = db.query(user_model.User).filter(user_model.User.user_name == user_name).first()
    
    # If the user is not found, raise an HTTP 404 error
    if not user:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail=f"User with user name {user_name} not found")
        
    return user

@router.get('/me/', response_model=user.UserInfo)
async def read_current_user(current_user: user.UserOut = Depends(oauth2.get_current_user)):
    """
    Get the currently authenticated user.

    Parameters:
    current_user (schemas.UserOut): The currently authenticated user.

    Returns:
    schemas.UserInfo: The user information.
    """
    return current_user

@router.get("/", response_model=List[user.UserInfo], include_in_schema=False)
async def read_users(db: AsyncSession = Depends(get_async_session)):
    """
    Retrieve a list of users.
    """
    query = select(user_model.User)
    result = await db.execute(query)
    users = result.scalars().all()
    return users



@router.post("/test", status_code=status.HTTP_201_CREATED, response_model=user.UserOut, include_in_schema=False)
async def created_user_test(user: user.UserCreateDel, db: AsyncSession = Depends(get_async_session)):

    # Hash the user's password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    # Create a new user and add it to the database
    new_user = user_model.User(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create a User_Status entry for the new user
    post = user_model.User_Status(user_id=new_user.id, user_name=new_user.user_name, name_room="Hell", room_id=1)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    return new_user