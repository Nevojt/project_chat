

from typing import List
from fastapi import Form, Response, status, HTTPException, Depends, APIRouter, UploadFile, File

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mail import send_mail


from app.config.config import settings
from app.config import utils
from app.routers.user.hello import say_hello_system, system_notification_change_owner
from app.routers.user.created_image import generate_image_with_letter
from app.auth import oauth2
from app.database.async_db import get_async_session

from app.models import models, user_model, room_model
from app.schemas import user


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin Users"],
)



@router.get("/company", response_model=List[user.UserInfoLights])
async def read_company_users(db: AsyncSession = Depends(get_async_session),
                             current_user: user.UserOut = Depends(oauth2.get_current_user)):
    
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to read users in this company")
    
    query_users = select(user_model.User).where(user_model.User.company_id == current_user.company_id)
    result = await db.execute(query_users)
    users = result.scalars().all()
    
    
    return users

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
    
    existing_deactivated_user = select(user_model.UserDeactivation).where((user_model.UserDeactivation.email == email) |
        (user_model.UserDeactivation.user_name == user_name))
    
    deactivated_result = await db.execute(existing_deactivated_user)
    existing_deactivated_user = deactivated_result.scalar_one_or_none()
    

    if existing_deactivated_user:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"User with email {email} or user_name {user_name} is deactivated")
    
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


@router.put("/{user_id}")
async def activated_deactivated_user(user_id: int,
                                     db: AsyncSession = Depends(get_async_session),
                                     current_user: int = Depends(oauth2.get_current_user)):
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to modify users")
        user_query = select(user_model.User).where(user_model.User.id == user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if user.active:
            user.active = False
            await db.commit()
            await db.refresh(user)
            return {f"User {user.user_name}": "Deactivated"}
            
        else:
            user.active = True
            await db.commit()
            await db.refresh(user)
            return {f"User {user.user_name}": "Activated"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error occurred while processing the request: {str(e)}")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivation_user(
    user_id: int,
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
    
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to delete users.")
        
        query = select(user_model.User).where(user_model.User.id == user_id)
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        # If the user does not exist, raise a 404 error
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with ID  does not exist.")

            
        query_room = select(room_model.Rooms).where(room_model.Rooms.owner == user_id)
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
                room.owner = current_user.id

        # Deactivate user
        deactivation = user_model.UserDeactivation(
                id=existing_user.id,
                email=existing_user.email,
                user_name=existing_user.user_name,
                reason=None,
                roles=None,
                company_id=existing_user.company_id
            )
        db.add(deactivation)
        
        await db.commit()

        
        # delete user
        await db.delete(existing_user)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error occurred while processing the request: {str(e)}")