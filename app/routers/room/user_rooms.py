from typing import List
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func, asc

from app.auth import oauth2
from app.database.database import get_db
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
    # message_and_user_counts = db.query(
    #     models.Socket.rooms.label('name_room'),
    #     func.count(models.Socket.id).label('count_messages'),
    #     func.count(models.User_Status.id).label('count_users')
    # ).join(models.User_Status, models.User_Status.name_room == models.Socket.rooms
    # ).group_by(models.Socket.rooms
    # ).filter(models.Socket.rooms != 'Hell').all()
    
    messages_count = db.query(
        models.Socket.rooms, 
        func.count(models.Socket.id).label('count')
    ).group_by(models.Socket.rooms).filter(models.Socket.rooms != 'Hell').all()

    # Count users for room
    users_count = db.query(
        models.User_Status.name_room, 
        func.count(models.User_Status.id).label('count')
    ).group_by(models.User_Status.name_room).filter(models.User_Status.name_room != 'Hell').all()

    rooms_info = []
    for room, favorite in rooms:
        # count_data = next((count for count in message_and_user_counts if count.name_room == room.name_room), None)
        room_info = room_schema.RoomFavorite(
            id=room.id,
            owner=room.owner,
            name_room=room.name_room,
            image_room=room.image_room,
            count_users= next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
            count_messages= next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
            created_at=room.created_at,
            secret_room=room.secret_room,
            favorite=favorite if favorite is not None else False,
            block=room.block
        )
        rooms_info.append(room_info)
        rooms_info.sort(key=lambda x: x.favorite, reverse=True)

    return rooms_info
    
    
    
    
@router.put("/{room_id}")  # Assuming you're using room_id
async def update_room_favorite(room_id: int, 
                                favorite: bool, 
                                db: Session = Depends(get_db), 
                                current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Updates the favorite status of a room for a specific user.

    Args:
        room_id (int): The ID of the room to update.
        favorite (bool): The new favorite status for the room.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (models.User, optional): The current user. Defaults to Depends(oauth2.get_current_user).

    Raises:
        HTTPException: If the user is blocked or not verified.
        HTTPException: If the room is not found.

    Returns:
        dict: A dictionary containing the room ID and the new favorite status.
    """  
    if current_user.blocked: # or not current_user.verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Access denied for user {current_user.id}")

    # Fetch room
    room = db.query(models.Rooms).filter(models.Rooms.id == room_id, models.Rooms.owner == current_user.id).first()
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    # Check if there is already a favorite record
    favorite_record = db.query(models.RoomsManagerMyRooms).filter(
        models.RoomsManagerMyRooms.room_id == room_id,
        models.RoomsManagerMyRooms.user_id == current_user.id
    ).first()

    # Update if exists, else create a new record
    if favorite_record:
        favorite_record.favorite = favorite
    else:
        new_favorite = models.RoomsManagerMyRooms(
            user_id=current_user.id, 
            room_id=room_id, 
            favorite=favorite
        )
        db.add(new_favorite)

    db.commit()
    return {"room_id": room_id, "favorite": favorite}
    



