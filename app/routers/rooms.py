from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.future import select
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_async_session
from .. import models, schemas, oauth2

router = APIRouter(
    prefix="/rooms",
    tags=['Rooms'],
)


@router.get("/", response_model=List[schemas.RoomBase])
async def get_rooms_info(db: Session = Depends(get_db)):
    
    """
    Retrieves information about chat rooms, excluding a specific room ('Hell'), along with associated message and user counts.

    Args:
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Returns:
        List[schemas.RoomBase]: A list containing information about each room, such as room name, image, count of users, count of messages, and creation date.
    """
    
    # get info rooms and not room "Hell"
    rooms = db.query(models.Rooms).filter(models.Rooms.name_room != 'Hell').all()

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
            "name_room": room.name_room,
            "image_room": room.image_room,
            "count_users": next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
            "count_messages": next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
            "created_at": room.created_at
        }
        rooms_info.append(schemas.RoomBase(**room_info))

    return rooms_info



@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_room(room: schemas.RoomCreate, db: AsyncSession = Depends(get_async_session), current_user: str = Depends(oauth2.get_current_user)):
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
    
    new_room = models.Rooms(**room.model_dump())
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    return new_room



@router.get("/{name_room}", response_model=schemas.RoomPost)
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


@router.delete("/{name_room}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(name_room: str, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    """Deletes a room.

    Args:
        name_room (str): The name of the room to delete.
        db (Session): The database session.
        current_user (str): The currently authenticated user.

    Raises:
        HTTPException: If the user does not have sufficient permissions.

    Returns:
        Response: An empty response with status code 204 No Content.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    room = db.query(models.Rooms).filter(models.Rooms.name_room == name_room)
    
    if room.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with: {name_room} not found")
    
    room.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)





# @router.put("/{name_room}")
# def update_room(name_room: str, update_post: schemas.RoomCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    
#     post_query = db.query(models.Rooms).filter(models.Rooms.name_room == name_room)
#     post = post_query.first()
    
#     if post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with name_room: {name_room} not found")
    
#     post_query.update(update_post.model_dump(), synchronize_session=False)
    
#     db.commit()
#     return {"Message": f"Room {name_room} update"}