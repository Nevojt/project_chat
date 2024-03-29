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
    prefix="/rooms",
    tags=['Rooms'],
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
    rooms = db.query(models.Rooms).filter(models.Rooms.name_room != 'Hell', models.Rooms.secret_room != True).order_by(asc(models.Rooms.id)).all()

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
            "secret_room": room.secret_room
        }
        rooms_info.append(room_schema.RoomBase(**room_info))

    return rooms_info

 

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_room(room: room_schema.RoomCreate, 
                      db: AsyncSession = Depends(get_async_session), 
                      current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Create a new room.

    Args:
        room (schemas.RoomCreate): Room creation data.
        db (AsyncSession): Database session.
        current_user (str): Currently authenticated user.

    Raises:
        HTTPException: If the room already exists.

    Returns:
        models.Rooms: The newly created room.
    """
    
    room_get = select(models.Rooms).where(models.Rooms.name_room == room.name_room)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    if existing_room:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"Room {room.name_room} already exists")
    
    new_room = models.Rooms(owner=current_user.id, **room.model_dump())
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    
    manager_room = models.RoomsManager(user_id=current_user.id, room_id=new_room.id)
    db.add(manager_room)
    await db.commit()
    await db.refresh(manager_room)
    
    return new_room



@router.get("/{name_room}", response_model=room_schema.RoomUpdate)
async def get_room(name_room: str, db: Session = Depends(get_db)):
    """
    Get a specific room by name.

    Parameters:
    name_room (str): The name of the room to retrieve.
    db (Session): The database session.

    Returns:
    schemas.RoomPost: The room with the specified name, or a 404 Not Found error if no room with that name exists.
    """
    post = db.query(models.Rooms).filter(models.Rooms.name_room == name_room).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with name_room: {name_room} not found")
    return post


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """Deletes a room.

    Args:
        room_id (int): The name of the room to delete.
        db (Session): The database session.
        current_user (str): The currently authenticated user.

    Raises:
        HTTPException: If the user does not have sufficient permissions.

    Returns:
        Response: An empty response with status code 204 No Content.
    """
    room = db.query(models.Rooms).filter(models.Rooms.id == room_id).first()
    
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")

    if current_user.role != "admin" and current_user.id != room.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Updating user statuses
    users_in_room = db.query(models.User_Status).filter(models.User_Status.room_id == room_id).all()
    for user_status in users_in_room:
        user_status.name_room = 'Hell'
        user_status.room_id = 1  # Assuming 'Hell' room ID is 1
        db.add(user_status)
    
    # Deleting the room
    db.delete(room)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{room_id}", response_model=room_schema.RoomUpdate)  # Assuming you're using room_id
def update_room(room_id: int, 
                update: room_schema.RoomCreate, 
                db: Session = Depends(get_db), 
                current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Update a room.

    Args:
        room_id (int): The ID of the room to update.
        update (schemas.RoomCreate): The updated room data.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Raises:
        HTTPException: If the room does not exist, or the user does not have sufficient permissions.

    Returns:
        JSON: A JSON object with a "Message" key containing a message indicating that the room was updated.
    """
    room_query = db.query(models.Rooms).filter(models.Rooms.id == room_id)
    room = room_query.first()
    
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID: {room_id} not found")
        
    if current_user.role != "admin" and current_user.id != room.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Assuming update.model_dump() returns a dictionary of attributes to update
    room_query.update(update.model_dump(), synchronize_session=False)
    
    db.commit()

    # Re-fetch or update the room object to reflect the changes
    updated_room = room_query.first()
    return updated_room

