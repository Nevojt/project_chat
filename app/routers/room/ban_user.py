from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.async_db import get_async_session
from datetime import datetime, timedelta
import pytz
from app.auth import oauth2
from app.models import models



router = APIRouter(
    prefix="/mute",
    tags=['Mute Users']
)

@router.post('/mute-user')
async def mute_user(user_id: int, room_id: int, duration_minutes: int, 
                    db: AsyncSession = Depends(get_async_session), 
                    current_user: models.User = Depends(oauth2.get_current_user)):

    if duration_minutes < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Duration must be a positive integer.")
        
    current_time_utc = datetime.now(pytz.timezone('UTC'))
    
    current_time_naive = current_time_utc.replace(tzinfo=None)
    
    room_get = select(models.Rooms).where(models.Rooms.id == room_id)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    if not existing_room or existing_room.owner != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of this room.")
                
    end_time = current_time_naive + timedelta(minutes=duration_minutes)
    ban = models.Ban(user_id=user_id, room_id=room_id, start_time=current_time_naive, end_time=end_time)
    
    db.add(ban)
    await db.commit()
    
    return {"message": f"User {user_id} has been muted for {duration_minutes} minutes"}


@router.delete('/un-mute-user')
async def un_mute_user(user_id: int, room_id: int, 
                    db: AsyncSession = Depends(get_async_session), 
                    current_user: models.User = Depends(oauth2.get_current_user)):
    
    
    delete_ban = select(models.Ban).where(models.Ban.user_id == user_id, models.Ban.room_id == room_id)
    result = await db.execute(delete_ban)
    existing_ban = result.scalar()
    
    if not existing_ban:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {user_id} is not muted in room {room_id}")
        
    await db.delete(existing_ban)
    await db.commit()
    
    return {"message": f"User {user_id} has been un-muted in room {room_id}"}