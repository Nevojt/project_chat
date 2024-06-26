from typing import List
from fastapi import File, Form, Query, UploadFile, status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, asc
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.database.database import get_db
from app.database.async_db import get_async_session

import shutil
import random
import string
import os
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from tempfile import NamedTemporaryFile

from app.models import models
from app.schemas import room as room_schema
from app.config.config import settings





info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", settings.backblaze_id, settings.backblaze_key)

router = APIRouter(
    prefix="/rooms",
    tags=['All Rooms'],
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
    # rooms = db.query(models.Rooms).filter(models.Rooms.name_room != 'Hell', models.Rooms.secret_room != True).order_by(asc(models.Rooms.id)).all()
    rooms = db.query(
        models.Rooms.id,
        models.Rooms.owner,
        models.Rooms.name_room,
        models.Rooms.image_room,
        models.Rooms.created_at,
        models.Rooms.secret_room,
        models.Rooms.block,
        models.Rooms.delete_at,
        func.count(models.Socket.id).label('count_messages')
    ).outerjoin(models.Socket, models.Rooms.name_room == models.Socket.rooms) \
    .filter(models.Rooms.name_room != 'Hell', models.Rooms.secret_room != True) \
    .group_by(models.Rooms.id) \
    .order_by(desc('count_messages')) \
    .all()
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
    if current_user.blocked == True or current_user.verified == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")
        
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
    
    role_in_room = models.RoleInRoom(user_id=current_user.id, room_id=new_room.id, role="owner")
    db.add(role_in_room)
    await db.commit()
    await db.refresh(role_in_room)
    
    add_room_to_my_room = models.RoomsManagerMyRooms(user_id=current_user.id, room_id=new_room.id)
    db.add(add_room_to_my_room)
    await db.commit()
    await db.refresh(add_room_to_my_room)
    
    if  room.secret_room == True:
        manager_room = models.RoomsManager(user_id=current_user.id, room_id=new_room.id)
        db.add(manager_room)
        await db.commit()
        await db.refresh(manager_room)
    
    return new_room


@router.post("/v2", status_code=status.HTTP_201_CREATED)
async def create_room_v2(name_room: str =Form(...),
                        file: UploadFile = File(...),
                        secret: bool = False,
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
    room_data = room_schema.RoomCreateV2(name_room=name_room, secret_room=secret)
    
    if current_user.blocked == True or current_user.verified == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")
        
    room_get = select(models.Rooms).where(models.Rooms.name_room == room_data.name_room)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    if existing_room:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"Room {room_data.name_room} already exists")
    
    image = await upload_to_backblaze(file)
    new_room = models.Rooms(owner=current_user.id, image_room=image, 
                            **room_data.model_dump())
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    
    role_in_room = models.RoleInRoom(user_id=current_user.id, room_id=new_room.id, role="owner")
    db.add(role_in_room)
    await db.commit()
    await db.refresh(role_in_room)
    
    add_room_to_my_room = models.RoomsManagerMyRooms(user_id=current_user.id, room_id=new_room.id)
    db.add(add_room_to_my_room)
    await db.commit()
    await db.refresh(add_room_to_my_room)
    
    if  room_data.secret_room == True:
        manager_room = models.RoomsManager(user_id=current_user.id, room_id=new_room.id)
        db.add(manager_room)
        await db.commit()
        await db.refresh(manager_room)
    
    return new_room


def generate_random_suffix(length=8):
    """
    Генерує випадковий суфікс з букв і цифр.

    Parameters:
    length (int): Довжина суфіксу. Значення за замовчуванням - 8.

    Returns:
    str: Випадковий суфікс.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def generate_unique_filename(filename):
    """
    Генерує унікальну назву файлу, додаючи випадковий суфікс.

    Parameters:
    filename (str): Назва файлу.

    Returns:
    str: Унікальна назва файлу.
    """
    file_name, file_extension = os.path.splitext(filename)
    unique_suffix = generate_random_suffix()
    unique_filename = f"{file_name}_{unique_suffix}{file_extension}"
    return unique_filename

async def upload_to_backblaze(file: UploadFile) -> str:
    """
    Uploads a file to Backblaze B2 storage.

    Parameters:
    file (UploadFile): The file to be uploaded.

    Returns:
    str: The download URL of the uploaded file.

    Raises:
    HTTPException: If an error occurs during the upload process.
    """

    try:
        # Create a temporary file to store the uploaded file
        with NamedTemporaryFile(delete=False) as temp_file:
            # Copy the uploaded file to the temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Set the name of the bucket where the file will be uploaded
        bucket_name = settings.bucket_name_room_image
        # Get the bucket by its name
        bucket = b2_api.get_bucket_by_name(bucket_name)
        
        # Upload the file to the bucket
        unique_filename = generate_unique_filename(file.filename)
        
        # Завантаження файлу до Backblaze B2
        bucket.upload_local_file(
            local_file=temp_file_path,
            file_name=unique_filename
        )
        
        # Get the download URL of the uploaded file
        download_url = b2_api.get_download_url_for_file_name(bucket_name, unique_filename)
        return download_url
    except Exception as e:
        # Raise a HTTPException with a 500 status code and the error message
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Close the file after the upload process
        file.file.close()

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
    if current_user.blocked == True or current_user.verified == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")
    
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
async def update_room(room_id: int, 
                      update_room: room_schema.RoomCreate, 
                      db: AsyncSession = Depends(get_async_session), 
                      current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Update a room by ID.
    """
    if current_user.blocked or not current_user.verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Access denied for user {current_user.id}")

    # Fetch room
    room_query = await db.execute(select(models.Rooms).where(models.Rooms.id == room_id))
    room = room_query.scalar_one_or_none()
    
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")

    # Check user permissions
    if current_user.role != "admin" and current_user.id != room.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions to modify room")

    # Update the room with new data provided by update_room
    update_data = update_room.model_dump()
    for key, value in update_data.items():
        setattr(room, key, value)  # Dynamically set attributes based on model_dump output

    await db.commit()  # Commit changes
    await db.refresh(room)  # Refresh the instance to get updated values

    # Handle room secrecy logic if applicable
    manager_query = await db.execute(select(models.RoomsManager).where(models.RoomsManager.room_id == room_id))
    manager = manager_query.scalar_one_or_none()
    
    if update_room.secret_room:
        if manager is None:
            manager = models.RoomsManager(user_id=current_user.id, room_id=room_id)
            db.add(manager)
            await db.commit()
            await db.refresh(manager)

    elif update_room.secret_room == False:
        if manager is not None:
            await db.delete(manager)
            await db.commit()

    return room


@router.put('/block/{room_id}', status_code=status.HTTP_200_OK)
async def block_room(room_id: int, 
                     db: Session = Depends(get_db), 
                     current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Blocks or unblocks a room.

    Args:
        room_id (int): The ID of the room to block or unblock.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Raises:
        HTTPException: If the room does not exist or the user does not have sufficient permissions.

    Returns:
        JSON: A JSON object with a "message" key containing a message indicating that the room was blocked or unblocked.
    """
    if current_user.blocked == True or current_user.verified == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")

    room = db.query(models.Rooms).filter(models.Rooms.id == room_id).first()
    
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID: {room_id} not found")
        
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
    room.block = not room.block
    db.commit()
    
    status_text = "unblocked" if not room.block else "blocked"
    return {"message": f"Room with ID: {room_id} has been {status_text}"}