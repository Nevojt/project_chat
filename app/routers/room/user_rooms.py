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



@router.get("/", response_model=List[room_schema.RoomFavorite])
async def get_user_rooms(db: Session = Depends(get_db), 
                         current_user: models.User = Depends(oauth2.get_current_user)):
    
    """
    Retrieves information about chat rooms, excluding a specific room ('Hell'), along with associated message and user counts.

    Args:
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Returns:
        List[schemas.RoomBase]: A list containing information about each room, such as room name, image, count of users, count of messages, and creation date.
    """
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
        
    rooms = db.query(
        models.Rooms,
        models.RoomsManagerMyRooms.favorite.label('favorite')
    ).outerjoin(
        models.RoomsManagerMyRooms,
        (models.RoomsManagerMyRooms.room_id == models.Rooms.id) & (models.RoomsManagerMyRooms.user_id == current_user.id)
    ).filter(models.Rooms.name_room != 'Hell', models.Rooms.owner == current_user.id
    ).order_by(asc(models.Rooms.id)).all()
    

    # Fetch message and user count for each user-associated room
    message_and_user_counts = db.query(
        models.Socket.rooms.label('name_room'),
        func.count(models.Socket.id).label('count_messages'),
        func.count(models.User_Status.id).label('count_users')
    ).join(models.User_Status, models.User_Status.name_room == models.Socket.rooms
    ).group_by(models.Socket.rooms
    ).filter(models.Socket.rooms != 'Hell').all()

    rooms_info = []
    for room, favorite in rooms:
        count_data = next((count for count in message_and_user_counts if count.name_room == room.name_room), None)
        room_info = room_schema.RoomFavorite(
            id=room.id,
            owner=room.owner,
            name_room=room.name_room,
            image_room=room.image_room,
            count_users=count_data.count_users if count_data else 0,
            count_messages=count_data.count_messages if count_data else 0,
            created_at=room.created_at,
            secret_room=room.secret_room,
            favorite=favorite if favorite is not None else False,
            block=room.block
        )
        rooms_info.append(room_info)
        rooms_info.sort(key=lambda x: x.favorite, reverse=True)

    return rooms_info
    
    



