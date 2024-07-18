
from typing import List
from fastapi import Form, Response, status, HTTPException, Depends, APIRouter, UploadFile, File


import pytz
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mail import send_mail


from app.config.config import settings
from app.config import utils
from app.routers.user.hello import say_hello_system, system_notification_change_owner
from app.routers.user.created_image import generate_image_with_letter
from app.auth import oauth2
from app.database.async_db import get_async_session

from app.models import user_model, room_model
from app.schemas import user


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin Users"],
)



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=user.UserOut)
async def created_user_admin(email: str = Form(...),
                          user_name: str = Form(...),
                          password: str = Form(...),
                          file: UploadFile = File(None),
                          db: AsyncSession = Depends(get_async_session),
                          current_user: int = Depends(oauth2.get_current_user)):
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
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to create users")
    
    company = current_user.company_id
    
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
        avatar = await utils.upload_to_backblaze(settings.rout_image)
    else:
        avatar = await utils.upload_to_backblaze(file)
        
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