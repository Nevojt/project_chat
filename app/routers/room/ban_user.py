from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.database.async_db import get_async_session
from datetime import datetime, timedelta
import pytz
from app.auth import oauth2
from app.models import models



router = APIRouter(
    prefix="/mute",
    tags=['Mute Users']
)


@router.get('/mute-users/{room_id}')
async def list_mute_users(room_id: int, db: AsyncSession = Depends(get_async_session), 
                          current_user: models.User = Depends(oauth2.get_current_user)):

    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
        
    room_query = select(models.Rooms).where(models.Rooms.id == room_id)
    room_result = await db.execute(room_query)
    room = room_result.scalar_one_or_none()
    
    role_room = select(models.RoleInRoom).where(models.RoleInRoom.room_id == room_id,
                                                models.RoleInRoom.user_id == current_user.id)
    result = await db.execute(role_room)
    role_in_room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID: {room_id} not found")

    if (room.owner != current_user.id and (role_in_room is None or role_in_room.role != "moderator")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to view banned users in this room.")

    mute_users_query = select(models.Ban).options(joinedload(models.Ban.user)).where(models.Ban.room_id == room_id)
    result = await db.execute(mute_users_query)
    bans = result.scalars().all()

    if not bans:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No banned users found in room ID: {room_id}")

    users_info = [{
        "id": ban.user.id,
        "user_name": ban.user.user_name,
        "avatar": ban.user.avatar,
    } for ban in bans if ban.user]

    return users_info



@router.post('/mute-user')
async def mute_user(user_id: int, room_id: int, duration_minutes: int, 
                    db: AsyncSession = Depends(get_async_session), 
                    current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Mute a user in a specific room.

    Parameters:
    user_id (int): The ID of the user to be muted.
    room_id (int): The ID of the room where the user is to be muted.
    duration_minutes (int): The duration in minutes for which the user will be muted.
    db (AsyncSession): The database session for asynchronous operations.
    current_user (models.User): The current user making the request.

    Returns:
    dict: A dictionary containing a success message and the ID of the muted user.

    Raises:
    HTTPException: If the room does not exist, the user is not a moderator or owner of the room, or the user_id is not valid.
    """
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
    
    if duration_minutes < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Duration must be a positive integer.")
        
    current_time_utc = datetime.now(pytz.timezone('UTC'))
    current_time_naive = current_time_utc.replace(tzinfo=None)
    
    room_get = select(models.Rooms).where(models.Rooms.id == room_id)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    role_room = select(models.RoleInRoom).where(models.RoleInRoom.room_id == room_id,
                                                models.RoleInRoom.user_id == current_user.id)
    result = await db.execute(role_room)
    role_in_room = result.scalar_one_or_none()
    
    # Check if the role exists and is a moderator or owner
    if not existing_room or (existing_room.owner != current_user.id and (role_in_room is None or role_in_room.role != "moderator")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner or a moderator of this room.")
                
    end_time = current_time_naive + timedelta(minutes=duration_minutes)
    ban = models.Ban(user_id=user_id, room_id=room_id, start_time=current_time_naive, end_time=end_time)
    
    db.add(ban)
    await db.commit()
    
    return {"message": f"User {user_id} has been muted for {duration_minutes} minutes"}


@router.delete('/un-mute-user')
async def un_mute_user(user_id: int, room_id: int, 
                    db: AsyncSession = Depends(get_async_session), 
                    current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Un-mute a user in a specific room.

    Parameters:
    user_id (int): The ID of the user to be un-muted.
    room_id (int): The ID of the room where the user is to be un-muted.
    db (AsyncSession): The database session for asynchronous operations.
    current_user (models.User): The current user making the request.

    Returns:
    dict: A dictionary containing a success message.

    Raises:
    HTTPException: If the room does not exist, the user is not a moderator or owner of the room, or the user is not muted in the room.
    """
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
        
    room_query = select(models.Rooms).where(models.Rooms.id == room_id)
    room_result = await db.execute(room_query)
    room = room_result.scalar_one_or_none()
    
    role_room = select(models.RoleInRoom).where(models.RoleInRoom.room_id == room_id,
                                                models.RoleInRoom.user_id == current_user.id)
    result = await db.execute(role_room)
    role_in_room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID: {room_id} not found")
        
    # Check if the role exists and is a moderator or owner
    if (room.owner != current_user.id and (role_in_room is None or role_in_room.role != "moderator")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner or a moderator of this room.")

    
    delete_ban = select(models.Ban).where(models.Ban.user_id == user_id, models.Ban.room_id == room_id)
    result = await db.execute(delete_ban)
    existing_ban = result.scalar()
    
    if not existing_ban:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {user_id} is not muted in room {room_id}")
        
    await db.delete(existing_ban)
    await db.commit()
    
    return {"message": f"User {user_id} has been un-muted in room {room_id}"}