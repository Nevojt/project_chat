from datetime import datetime
from typing import List
from fastapi import Form, Response, status, HTTPException, Depends, APIRouter, UploadFile, File, Query
import shutil
import random
import string
import os
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from tempfile import NamedTemporaryFile

import pytz
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mail import send_mail

from ...config import utils
from app.config.config import settings
from .hello import say_hello_system
from ...auth import oauth2
from ...database.async_db import get_async_session
from ...database.database import get_db
from app.models import models
from app.schemas import user


info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", settings.backblaze_id, settings.backblaze_key)



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
    post = models.User_Status(user_id=new_user.id, user_name=new_user.user_name, name_room="Hell", room_id=1)
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
async def created_user_v2(email: str = Form(...), user_name: str = Form(...), password: str = Form(...),
                       file: UploadFile = File(...),
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

    user_data = user.UserCreateV2(email=email, user_name=user_name, password=password)

# Check if a user with the given email already exists
    email_query = select(models.User).where(models.User.email == user_data.email)
    email_result = await db.execute(email_query)
    existing_email_user = email_result.scalar_one_or_none()

    if existing_email_user:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"User with email {existing_email_user.email} already exists")
    
    # Check if a user with the given user_name already exists
    username_query = select(models.User).where(models.User.user_name == user_data.user_name)
    username_result = await db.execute(username_query)
    existing_username_user = username_result.scalar_one_or_none()

    if existing_username_user:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"User with user_name {existing_username_user.user_name} already exists")
    
    # Hash the user's password
    hashed_password = utils.hash(user_data.password)
    user_data.password = hashed_password
    
    verification_token = utils.generate_unique_token(user_data.email)
    avatar = await upload_to_backblaze(file)
    # Create a new user and add it to the database
    new_user = models.User(**user_data.model_dump(),
                           avatar=avatar,
                           token_verify=verification_token)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create a User_Status entry for the new user
    post = models.User_Status(user_id=new_user.id, user_name=new_user.user_name, name_room="Hell", room_id=1)
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

def generate_random_suffix(length=8):
    """
    Генерує випадковий суфікс з букв і цифр.

    Parameters:
    length (int): Довжина суфіксу. Значення за замовчуванням - 8.

    Returns:
    str: Випадковий суфікс.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def generate_unique_filename(filename):
    """
    Генерує унікальну назву файлу, додаючи випадковий суфікс.

    Parameters:
    filename (str): Назва файлу.

    Returns:
    str: Унікальна назва файлу.
    """
    file_name, file_extension = os.path.splitext(filename)
    unique_suffix = generate_random_suffix()
    unique_filename = f"{file_name}_{unique_suffix}{file_extension}"
    return unique_filename

async def upload_to_backblaze(file: UploadFile) -> str:
    """
    This function is responsible for uploading a file to a specified Backblaze B2 bucket.

    Parameters:
    file (UploadFile): The file to be uploaded. The file size limit is set to 25MB.
    bucket_name (str): The name of the Backblaze B2 bucket to upload the file to. The default value is "chatall".
                        Download avatars: bucket -> "usravatar"
                        The bucket_name must be one of the values in the 'bucket' list.

    Returns:
    str: The public URL of the uploaded file.
    
    Raises:
    HTTPException: If an error occurs during the upload process.
    """
    try:
        with NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        bucket_name = "usravatar"
        bucket = b2_api.get_bucket_by_name(bucket_name)
        
        unique_filename = generate_unique_filename(file.filename)
        
        # Завантаження файлу до Backblaze B2
        bucket.upload_local_file(
            local_file=temp_file_path,
            file_name=unique_filename
        )
        
        download_url = b2_api.get_download_url_for_file_name(bucket_name, unique_filename)
        return download_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()





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
    
    query = select(models.User).where(models.User.id == current_user.id)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    # Якщо користувач не існує, підніміть помилку 404
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with ID  does not exist.")
    # Перевірте, чи користувач верифікований
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
        
    query_room = select(models.Rooms).where(models.Rooms.owner == current_user.id)
    result_room = await db.execute(query_room)
    rooms_to_update = result_room.scalars().all()
    for room in rooms_to_update:
        room.owner = 0
        room.delete_at = datetime.now(pytz.utc)
        
    await db.commit()

    
    # Видаліть користувача
    await db.delete(existing_user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


     
        
@router.put('/', response_model=user.UserInfo)
async def update_user(update: user.UserUpdate, 
                      db: Session = Depends(get_db), 
                      current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Update a user's information.

    Args:
        update (schemas.UserUpdate): The updated user information.
        db (Session): The database session to use.
        current_user (models.User): The currently authenticated user.

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
        
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    user = user_query.first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID: {current_user.id} not found"
        )
    
    user_status_query = db.query(models.User_Status).filter(models.User_Status.user_id == current_user.id)
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
    user = db.query(models.User).filter(models.User.email == email).first()
    
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
    user = db.query(models.User).filter(models.User.user_name == user_name).first()
    
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
    query = select(models.User)
    result = await db.execute(query)
    users = result.scalars().all()
    return users
