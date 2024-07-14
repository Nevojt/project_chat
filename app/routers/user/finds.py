
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...database.database import get_db
from app.models import user_model, room_model, messages_model
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
    - `substring`: The substring to filter by. This parameter is case-insensitive.
    - `db`: The database session. It is injected by the `get_db` function.

    Returns:
    - A dictionary containing a list of users and rooms that match the search criteria.
      Each user is represented as a dictionary with the following keys:
      - `id`: The user's unique identifier.
      - `user_name`: The user's name.
      - `avatar`: The user's avatar URL.
      - `created_at`: The date and time when the user was created.
      Each room is represented as a dictionary with the following keys:
      - `id`: The room's unique identifier.
      - `owner`: The room's owner.
      - `name_room`: The room's name.
      - `image_room`: The room's image URL.
      - `count_users`: The number of users in the room.
      - `count_messages`: The number of messages in the room.
      - `created_at`: The date and time when the room was created.
      - `secret_room`: A boolean indicating whether the room is a secret room.

    The function uses SQLAlchemy's ORM to query the database and filter users and rooms based on the provided substring.
    It also counts the number of users and messages in each room.
    """
    pattern = f"%{substring.lower()}%"
    
    # Search for users
    users = db.query(user_model.User).filter(func.lower(user_model.User.user_name).like(pattern)).all()
    
    # Search for rooms
    rooms = db.query(room_model.Rooms).filter(
        room_model.Rooms.name_room != 'Hell', 
        room_model.Rooms.secret_room != True, 
        func.lower(room_model.Rooms.name_room).like(pattern)
    ).all()

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
    
@router.get("/users/{substring}")
def search_users(substring: str, db: Session = Depends(get_db)):
    """
    Search for users based on a substring.

    Parameters:
    - `substring`: The substring to filter by. This parameter is case-insensitive.
    - `db`: The database session. It is injected by the `get_db` function.

    Returns:
    - A dictionary containing a list of users that match the search criteria.
      Each user is represented as a dictionary with the following keys:
      - `id`: The user's unique identifier.
      - `user_name`: The user's name.
      - `avatar`: The user's avatar URL.
      - `created_at`: The date and time when the user was created.

    The function uses SQLAlchemy's ORM to query the database and filter users based on the provided substring.
    """
    pattern = f"%{substring.lower()}%"
    
    # Search for users
    users = db.query(user_model.User).filter(func.lower(user_model.User.user_name).like(pattern)).all()
    
    users_info =[]
    for user in users:
        user_info = {
            "id": user.id,
            "user_name": user.user_name,
            "avatar": user.avatar,
            "created_at": user.created_at
        }
        users_info.append(user_schema.UserOut(**user_info))
    
    return {"users": users_info}