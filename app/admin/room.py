from datetime import datetime
from typing import List
from fastapi import Form, Response, status, HTTPException, Depends, APIRouter, UploadFile, File


import pytz
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mail import send_mail
from app.models import room_model, room_model, messages_model, user_model
from app.schemas import room as room_schema

from app.config.config import settings
from app.config import utils
from app.routers.user.hello import say_hello_system, system_notification_change_owner
from app.routers.user.created_image import generate_image_with_letter
from app.auth import oauth2
from app.database.async_db import get_async_session
from app.database.database import get_db

from app.models import user_model, room_model
from app.schemas import user


router = APIRouter(
    prefix="/admin/rooms",
    tags=["Admin Rooms"],
)



@router.get("/", response_model=List[room_schema.RoomBase])
async def get_rooms_info(db: Session = Depends(get_db)):
    
    """
    Retrieves information about chat rooms, excluding a specific room ('Hell'), along with associated message and user counts.

    Args:
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Returns:
        List[schemas.RoomBase]: A list containing information about each room, such as room name, image, count of users, count of messages, and creation date.
    """
    
    # get info rooms and not room "Hell"
    # rooms = db.query(room_model.Rooms).filter(room_model.Rooms.name_room != 'Hell', room_model.Rooms.secret_room != True).order_by(asc(room_model.Rooms.id)).all()
    rooms = db.query(
        room_model.Rooms.id,
        room_model.Rooms.owner,
        room_model.Rooms.name_room,
        room_model.Rooms.image_room,
        room_model.Rooms.created_at,
        room_model.Rooms.secret_room,
        room_model.Rooms.block,
        room_model.Rooms.delete_at,
        func.count(messages_model.Socket.id).label('count_messages')
    ).outerjoin(messages_model.Socket, room_model.Rooms.name_room == messages_model.Socket.rooms) \
    .filter(room_model.Rooms.name_room != 'Hell', room_model.Rooms.secret_room != True) \
    .group_by(room_model.Rooms.id) \
    .order_by(desc('count_messages')) \
    .all()
    # Count messages for room
    messages_count = db.query(
        messages_model.Socket.rooms, 
        func.count(messages_model.Socket.id).label('count')
    ).group_by(messages_model.Socket.rooms).filter(messages_model.Socket.rooms != 'Hell').all()

    # Count users for room
    users_count = db.query(
        user_model.User_Status.name_room, 
        func.count(user_model.User_Status.id).label('count')
    ).group_by(user_model.User_Status.name_room).filter(user_model.User_Status.name_room != 'Hell').all()

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


