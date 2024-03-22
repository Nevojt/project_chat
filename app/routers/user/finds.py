
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

# from typing import List
from ...database.database import get_db
from app.models import models
from app.schemas import user as user_schema
from app.schemas import room as schema_room


router = APIRouter(
    prefix="/search",
    tags=['Search'],
)

@router.get('/{substring}')
def search_users_and_rooms(substring: str, db: Session = Depends(get_db)):
    """
    Search for users and rooms based on a substring.

    Parameters:
    - `substring`: The substring to filter by.

    Returns:
    - A dictionary containing two lists: one for users and one for rooms.
    """
    pattern = f"%{substring.lower()}%"
    
    # Search for users
    users = db.query(models.User).filter(func.lower(models.User.user_name).like(pattern)).all()
    
    # Search for rooms
    rooms = db.query(models.Rooms).filter(
        models.Rooms.name_room != 'Hell', 
        models.Rooms.secret_room != True, 
        func.lower(models.Rooms.name_room).like(pattern)
    ).all()

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
    
    
    users_info =[]
    for user in users:
        user_info = {
            "id": user.id,
            "user_name": user.user_name,
            "avatar": user.avatar,
            "created_at": user.created_at
        }
        users_info.append(user_schema.UserOut(**user_info))

    # Prepare room info
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
            "secret_room": room.secret_room
        }
        rooms_info.append(schema_room.RoomBase(**room_info))
    
    # Return the results
    return {
        "users": users_info,
        "rooms": rooms_info
    }