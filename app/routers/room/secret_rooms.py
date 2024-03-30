from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, asc
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.database.database import get_db
from app.database.async_db import get_async_session

from app.models import models
from app.schemas import room as room_schema

router = APIRouter(
    prefix='/secret',
    tags=['Secret Rooms'],
)



@router.get("/")
async def get_user_rooms_secret(db: Session = Depends(get_db), 
                              current_user: models.User = Depends(oauth2.get_current_user)) -> List[room_schema.RoomFavorite]:
    """
    Retrieve a list of rooms accessible by the current user, along with their associated message and user counts.

    Args:
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        List[room_schema.RoomBase]: A list of room information, including name, image, user count, message count, and creation date.
    """
    
    # Fetch room IDs for the current user
    user_room_ids = db.query(models.RoomsManager.room_id).filter(models.RoomsManager.user_id == current_user.id).all()
    user_room_ids = [str(room_id[0]) for room_id in user_room_ids]  # Extracting room IDs from the tuple

    # Query rooms details based on user_room_ids, excluding 'Hell'
    rooms = db.query(models.Rooms, models.RoomsManager.favorite
                     ).filter(models.Rooms.id.in_(user_room_ids), 
                    models.Rooms.name_room != 'Hell',
                    models.Rooms.secret_room == True,
                    models.RoomsManager.room_id == models.Rooms.id,  # Ensure the mapping between Rooms and RoomsManager
                    models.RoomsManager.user_id == current_user.id  # Ensure we're getting the favorite status for the current user
    ).all()

    # Fetch message count for each user-associated room
    messages_count = db.query(
        models.Socket.rooms, 
        func.count(models.Socket.id).label('count')
    ).group_by(models.Socket.rooms).filter(models.Socket.rooms.in_(user_room_ids)).all()

    # Fetch user count for each user-associated room
    users_count = db.query(
        models.User_Status.name_room, 
        func.count(models.User_Status.id).label('count')
    ).group_by(models.User_Status.name_room).filter(models.User_Status.name_room.in_(user_room_ids)).all()

    # Merging room info, message count, and user count
    rooms_info = []
    for room, favorite in rooms:
        room_info = {
            "id": room.id,
            "owner": room.owner,
            "name_room": room.name_room,
            "image_room": room.image_room,
            "count_users": next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
            "count_messages": next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
            "created_at": room.created_at,
            "secret_room": room.secret_room,
            "favorite": favorite
        }
        rooms_info.append(room_schema.RoomFavorite(**room_info))
        rooms_info.sort(key=lambda x: x.favorite, reverse=True)

    return rooms_info
    
    
@router.post('/add_user')
async def toggle_user_in_room(room_id: int, user_id: int, 
                              db: AsyncSession = Depends(get_async_session), 
                              current_user: models.User = Depends(oauth2.get_current_user)):

    # Перевірка чи існує кімната і чи є поточний користувач її власником
    room_get = select(models.Rooms).where(models.Rooms.id == room_id,
                                          models.Rooms.owner == current_user.id,
                                          models.Rooms.secret_room == True)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()

    if existing_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")

    # Перевірка чи користувач вже є у кімнаті
    manager_room_query = select(models.RoomsManager).where(
        models.RoomsManager.user_id == user_id,
        models.RoomsManager.room_id == room_id
    )
    existing_manager_room = await db.execute(manager_room_query)
    manager_room = existing_manager_room.scalar_one_or_none()

    # Додавання або видалення користувача з кімнати
    if manager_room:
        await db.delete(manager_room)
        await db.commit()
        return {"message": "User removed from the room"}
    else:
        new_manager_room = models.RoomsManager(user_id=user_id, room_id=room_id)
        db.add(new_manager_room)
        await db.commit()
        await db.refresh(new_manager_room)
        return {"message": "User added to the room"}


@router.put('/{room_id}')
async def favorite_room(room_id: int, 
                        db: AsyncSession = Depends(get_async_session), 
                        current_user: models.User = Depends(oauth2.get_current_user)):
    """

    """
    
    room_get = select(models.Rooms).where(models.Rooms.id == room_id, models.Rooms.secret_room == True)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    if existing_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")
        
    manager_room_query = select(models.RoomsManager).where(
        models.RoomsManager.user_id == current_user.id,
        models.RoomsManager.room_id == room_id
    )
    existing_manager_room = await db.execute(manager_room_query)
    manager_room = existing_manager_room.scalar_one_or_none()
    if manager_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")
    
    if manager_room.favorite == True:
        manager_room.favorite = False
    else:
        manager_room.favorite = True

    await db.commit()
    await db.refresh(manager_room)

    return {"favorite": manager_room.favorite}
