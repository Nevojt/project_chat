
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from typing import List
from ...database.database import get_db
from app.models import models
from app.schemas import user
from app.schemas import room as schema_room


router = APIRouter(
    prefix="/search",
    tags=['Search'],
)

@router.get('/user/{substring}', response_model=List[user.UserInfo])
def get_user_name(substring: str, db: Session = Depends(get_db)):
    """
    Get a list of users filtered by a substring.

    Parameters:
    - `substring`: The substring to filter by.

    Returns:
    - A list of users that match the given substring.

    Raises:
    - HTTPException 404 if no users match the given substring.
    """
    
    pattern = f"{substring.lower()}%"  # Matches any username starting with 'substring'
    # Query the database for a user with the given username
    user = db.query(models.User).filter(func.lower(models.User.user_name).like(pattern)).all()
    # If the user is not found, raise an HTTP 404 error
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {pattern} not found")
        
    return user

@router.get('/room/{substring}', response_model=List[schema_room.RoomBase])
def get_rooms(substring: str, db: Session = Depends(get_db)):
    """
    Get a list of rooms filtered by a substring.

    Parameters:
    - `substring`: The substring to filter by.

    Returns:
    - A list of rooms that match the given substring.

    Raises:
    - HTTPException 404 if no rooms match the given substring.
    """
    
    pattern = f"{substring.lower()}%"
    rooms = db.query(models.Rooms).filter(models.Rooms.name_room != 'Hell', models.Rooms.private != True, func.lower(models.Rooms.name_room).like(pattern)).all()

    if not rooms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room {pattern} not found")
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
            "private": room.private
        }
        rooms_info.append(schema_room.RoomBase(**room_info))
        
    return rooms_info