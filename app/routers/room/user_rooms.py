from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, asc
# from sqlalchemy.future import select
# from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.database.database import get_db
# from app.database.async_db import get_async_session

from app.models import models
from app.schemas import room as room_schema

router = APIRouter(
    prefix='/user_rooms',
    tags=['User rooms'],
)



@router.get("/", response_model=List[room_schema.RoomBase])
async def get_user_rooms(db: Session = Depends(get_db), 
                         current_user: models.User = Depends(oauth2.get_current_user)):
    
    """
    Retrieves information about chat rooms, excluding a specific room ('Hell'), along with associated message and user counts.

    Args:
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Returns:
        List[schemas.RoomBase]: A list containing information about each room, such as room name, image, count of users, count of messages, and creation date.
    """
    
    # get info rooms and not room "Hell"
    rooms = db.query(models.Rooms).filter(models.Rooms.name_room != 'Hell',
                                          models.Rooms.owner == current_user.id).order_by(asc(models.Rooms.id)).all()

    # Count messages for room
    messages_count = db.query(
        models.Socket.rooms, 
        func.count(models.Socket.id).label('count')
    ).group_by(models.Socket.rooms).filter(models.Socket.rooms != 'Hell').all()

    # Count users for room
    users_count = db.query(
        models.User_Status.name_room, 
        func.count(models.User_Status.id).label('count')
    ).group_by(models.User_Status.name_room).filter(models.User_Status.name_room != 'Hell').all()

    # merge result
    rooms_info = []
    for room in rooms:
        room_info = {
            "id": room.id,
            "owner": room.owner,
            "name_room": room.name_room,
            "image_room": room.image_room,
            "count_users": next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
            "count_messages": next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
            "created_at": room.created_at,
            "secret_room": room.secret_room,
            "block": room.block
        }
        rooms_info.append(room_schema.RoomBase(**room_info))

    return rooms_info
    
    



