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
    prefix='/tabs',
    tags=['Tabs User'],
)



# @router.get("/")
# async def get_user_tabs(db: Session = Depends(get_db), 
#                               current_user: models.User = Depends(oauth2.get_current_user)) -> List[room_schema.RoomTabs]:
    
#     all_tabs = db.query(models.RoomsTabs).filter(models.RoomsTabs.user_id == current_user.id).all()
    
#     return all_tabs

@router.get("/")
async def get_user_tabs(db: Session = Depends(get_db), 
                              current_user: models.User = Depends(oauth2.get_current_user)) -> dict:

    # Fetch rooms and tabs details for the current user
    rooms_and_tabs = db.query(models.Rooms, models.RoomsTabs
        ).filter(models.RoomsTabs.user_id == current_user.id,
                 models.Rooms.id == models.RoomsTabs.room_id).all()
         
    
#     # Fetch message count for each user-associated room
    messages_count = db.query(
        models.Socket.rooms, 
        func.count(models.Socket.id).label('count')
    ).group_by(models.Socket.rooms).filter(models.Socket.rooms != 'Hell').all()

    # Count users for room
    users_count = db.query(
        models.User_Status.name_room, 
        func.count(models.User_Status.id).label('count')
    ).group_by(models.User_Status.name_room).filter(models.User_Status.name_room != 'Hell').all()


    # Initialize an empty dictionary to store tabs with their associated rooms
    tabs_with_rooms = {}

    # Iterate over each room and tab pair
    for room, tab in rooms_and_tabs:
        room_info = {
            "id": room.id,
            "owner": room.owner,
            "name_room": room.name_room,
            "image_room": room.image_room,
            "count_users": next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
            "count_messages": next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
            "created_at": room.created_at,
            "secret_room": room.secret_room,
            "favorite": tab.favorite,
            "block": room.block,
            
            # Add any other room details you want to include
        }

        # If the tab name isn't in the dictionary, add it with an empty list
        if tab.tab_name not in tabs_with_rooms:
            tabs_with_rooms[tab.tab_name] = []

        # Append room info to the correct tab
        tabs_with_rooms[tab.tab_name].append(room_info)
        
        # Sort the rooms in each tab based on their favorite status
        for tab_name, rooms in tabs_with_rooms.items():
            rooms.sort(key=lambda x: x['favorite'], reverse=True)
        

    return tabs_with_rooms














# @router.get("/")
# async def get_user_tabs(db: Session = Depends(get_db), 
#                               current_user: models.User = Depends(oauth2.get_current_user)) -> List[room_schema.RoomTabs]:

    
#     # Fetch room IDs for the current user
#     user_room_ids = db.query(models.RoomsTabs.room_id).filter(models.RoomsTabs.user_id == current_user.id).all()
#     user_room_ids = [str(room_id[0]) for room_id in user_room_ids]  # Extracting room IDs from the tuple

#     # Query rooms details based on user_room_ids, excluding 'Hell'
#     rooms = db.query(models.Rooms, models.RoomsTabs.favorite
#                      ).filter(models.Rooms.id.in_(user_room_ids), 
#                     models.Rooms.name_room != 'Hell',
#                     models.Rooms.secret_room == False,
#                     models.RoomsTabs.room_id == models.Rooms.id,  # Ensure the mapping between Rooms and RoomsTabs
#                     models.RoomsTabs.user_id == current_user.id  # Ensure we're getting the favorite status for the current user
#     ).all()

#     # Fetch message count for each user-associated room
#     messages_count = db.query(
#         models.Socket.rooms, 
#         func.count(models.Socket.id).label('count')
#     ).group_by(models.Socket.rooms).filter(models.Socket.rooms.in_(user_room_ids)).all()

#     # Fetch user count for each user-associated room
#     users_count = db.query(
#         models.User_Status.name_room, 
#         func.count(models.User_Status.id).label('count')
#     ).group_by(models.User_Status.name_room).filter(models.User_Status.name_room.in_(user_room_ids)).all()

#     # Merging room info, message count, and user count
#     rooms_info = []
#     for room, favorite in rooms:
#         room_info = {
#             "id": room.id,
#             "owner": room.owner,
#             "name_room": room.name_room,
#             "image_room": room.image_room,
#             "count_users": next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
#             "count_messages": next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
#             "created_at": room.created_at,
#             "secret_room": room.secret_room,
#             "favorite": favorite
#         }
#         rooms_info.append(room_schema.RoomFavorite(**room_info))
#         rooms_info.sort(key=lambda x: x.favorite, reverse=True)

#     return rooms_info























# @router.post('/add_room')
# async def toggle_room_in_favorites(room_id: int, 
#                                    db: AsyncSession = Depends(get_async_session), 
#                                    current_user: models.User = Depends(oauth2.get_current_user)):
#     """
#     Toggles a room as a favorite for the current user.

#     Args:
#         room_id (int): The ID of the room to toggle.
#         db (AsyncSession): The database session.
#         current_user (models.User): The currently authenticated user.

#     Raises:
#         HTTPException: If the room does not exist or the user does not have sufficient permissions.

#     Returns:
#         JSON: A JSON object with a "message" key indicating whether the room was added or removed from the user's favorites.
#     """
    
#     room_get = select(models.Rooms).where(models.Rooms.id == room_id)
#     result = await db.execute(room_get)
#     existing_room = result.scalar_one_or_none()
    
#     if existing_room is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Room with ID {room_id} not found")

#     manager_room_query = select(models.RoomsTabs).where(
#         models.RoomsTabs.user_id == current_user.id,
#         models.RoomsTabs.room_id == room_id
#     )
#     existing_manager_room = await db.execute(manager_room_query)
#     manager_room = existing_manager_room.scalar_one_or_none()

#     if manager_room:
#         await db.delete(manager_room)
#     else:
#         new_manager_room = models.RoomsTabs(user_id=current_user.id, room_id=room_id)
#         db.add(new_manager_room)
    
#     await db.commit()

#     if manager_room:
#         return {"message": "Room removed from favorites"}
#     else:
#         await db.refresh(new_manager_room)
#         return new_manager_room
    
    
# @router.post('/add_user')
# async def toggle_user_in_favorite_room(room_id: int, user_id: int, 
#                               db: AsyncSession = Depends(get_async_session), 
#                               current_user: models.User = Depends(oauth2.get_current_user)):

#     # audit room and user from owner room 
#     room_get = select(models.Rooms).where(models.Rooms.id == room_id,
#                                           models.Rooms.owner == current_user.id,
#                                           models.Rooms.secret_room == False)
#     result = await db.execute(room_get)
#     existing_room = result.scalar_one_or_none()

#     if existing_room is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Room with ID {room_id} not found")

#     # Audit user in room
#     manager_room_query = select(models.RoomsTabs).where(
#         models.RoomsTabs.user_id == user_id,
#         models.RoomsTabs.room_id == room_id
#     )
#     existing_manager_room = await db.execute(manager_room_query)
#     manager_room = existing_manager_room.scalar_one_or_none()

#     # add or delete user for room
#     if manager_room:
#         await db.delete(manager_room)
#         await db.commit()
#         return {"message": "User removed from the room"}
#     else:
#         new_manager_room = models.RoomsTabs(user_id=user_id, room_id=room_id)
#         db.add(new_manager_room)
#         await db.commit()
#         await db.refresh(new_manager_room)
#         return {"message": "User added to the room"}


# @router.put('/{room_id}')
# async def update_favorite_room(room_id: int, 
#                         db: AsyncSession = Depends(get_async_session), 
#                         current_user: models.User = Depends(oauth2.get_current_user)):
#     """
#     Update the favorite status of a room.

#     Parameters:
#         room_id (int): The ID of the room to update.
#         db (AsyncSession): The database session.
#         current_user (models.User): The currently authenticated user.

#     Raises:
#         HTTPException: If the room does not exist or the user does not have sufficient permissions.

#     Returns:
#         JSON: A JSON object with a "favorite" key indicating the new favorite status of the room.

#     """
    
#     room_get = select(models.Rooms).where(models.Rooms.id == room_id, models.Rooms.secret_room != True)
#     result = await db.execute(room_get)
#     existing_room = result.scalar_one_or_none()
    
#     if existing_room is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Room with ID {room_id} not found")
        
#     manager_room_query = select(models.RoomsTabs).where(
#         models.RoomsTabs.user_id == current_user.id,
#         models.RoomsTabs.room_id == room_id
#     )
#     existing_manager_room = await db.execute(manager_room_query)
#     manager_room = existing_manager_room.scalar_one_or_none()
#     if manager_room is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Room with ID {room_id} not found")
    
#     if manager_room.favorite == True:
#         manager_room.favorite = False
#     else:
#         manager_room.favorite = True

#     await db.commit()
#     await db.refresh(manager_room)

#     return {"favorite": manager_room.favorite}
