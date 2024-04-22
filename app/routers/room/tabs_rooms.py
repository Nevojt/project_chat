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


@router.post('/')
async def create_user_tab(tab: room_schema.RoomTabsCreate, 
                          db: AsyncSession = Depends(get_async_session), 
                          current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Create a new tab for the current user.

    Args:
        tab (room_schema.RoomTabsCreate): A dictionary containing the details of the new tab.
        db (AsyncSession): The database session.
        current_user (models.User): The currently authenticated user.

    Raises:
        HTTPException: If the tab already exists or if there is an internal server error.

    Returns:
        JSON: A JSON object containing the details of the newly created tab.
    """

    try:
        # Check if tab already exists
        post_tab = select(models.RoomTabsInfo).where(models.RoomTabsInfo.name_tab == tab.name_tab)
        result = await db.execute(post_tab)
        existing_room = result.scalar_one_or_none()

        if existing_room:
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                                detail=f"Tab {tab.name_tab} already exists")
        
        # Create a new tab
        new_tab = models.RoomTabsInfo(owner_id=current_user.id, **tab.model_dump())
        db.add(new_tab)
        await db.commit()
        await db.refresh(new_tab)
        return new_tab

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))

    


@router.get("/")
async def get_user_all_rooms_in_all_tabs(db: Session = Depends(get_db), 
                                         current_user: models.User = Depends(oauth2.get_current_user)) -> dict:
    """
    Get all tabs for the current user.

    Args:
        db (Session): The database session.
        current_user (models.User): The currently authenticated user.

    Returns:
        List[room_schema.RoomTabs]: A list of tabs for the current user.
    """
    # Fetch all tabs for the current user
    user_tabs = db.query(models.RoomTabsInfo).filter(models.RoomTabsInfo.owner_id == current_user.id).all()

    # Create a dictionary for each tab with an empty room list
    tabs_with_rooms = {tab.name_tab: {"name_tab": tab.name_tab, "image_tab": tab.image_tab, "id": tab.id, "rooms": []} for tab in user_tabs}

    # Fetch rooms and tabs details for the current user
    rooms_and_tabs = db.query(models.Rooms, models.RoomsTabs
        ).join(models.RoomsTabs, models.Rooms.id == models.RoomsTabs.room_id
        ).filter(models.RoomsTabs.user_id == current_user.id).all()

    # Fetch message count for each user-associated room
    messages_count = db.query(
        models.Socket.rooms, 
        func.count(models.Socket.id).label('count')
    ).group_by(models.Socket.rooms).filter(models.Socket.rooms != 'Hell').all()

    # Count users for room
    users_count = db.query(
        models.User_Status.name_room, 
        func.count(models.User_Status.id).label('count')
    ).group_by(models.User_Status.name_room).filter(models.User_Status.name_room != 'Hell').all()

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
            "block": room.block
        }
        
        # Append room info to the correct tab
        tabs_with_rooms[tab.tab_name]["rooms"].append(room_info)

    # Sort rooms in each tab
    for tab_name in tabs_with_rooms:
        tabs_with_rooms[tab_name]["rooms"].sort(key=lambda x: x['favorite'], reverse=True)

    return tabs_with_rooms




@router.get('/{tab}')
async def get_rooms_in_one_tab(db: Session = Depends(get_db), 
                              current_user: models.User = Depends(oauth2.get_current_user),
                              tab: str = None):
    """
    Get all rooms in a specific tab.

    Args:
        db (Session): The database session.
        current_user (models.User): The currently authenticated user.
        tab (str): The name of the tab.

    Returns:
        List[room_schema.RoomTabs]: A list of rooms in the specified tab.

    Raises:
        HTTPException: If the tab does not exist.
    """

    tab_exists = db.query(models.RoomTabsInfo).filter(models.RoomTabsInfo.owner_id == current_user.id, 
                                                      models.RoomTabsInfo.name_tab == tab).first()
    if not tab_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tab {tab} not found"
        )

    # Fetch rooms and tabs details for the current user in the specified tab
    rooms_and_tabs = db.query(models.Rooms, models.RoomsTabs
        ).join(models.RoomsTabs, models.Rooms.id == models.RoomsTabs.room_id
        ).filter(models.RoomsTabs.user_id == current_user.id,
                 models.RoomsTabs.tab_name == tab).all()
         
    # Fetch message count for each user-associated room
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
     # Prepare room details
    room_details = []
    for room, tab_info in rooms_and_tabs:
        room_info = {
            "id": room.id,
            "owner": room.owner,
            "name_room": room.name_room,
            "image_room": room.image_room,
            "count_users": 0,  # Initialize count of users
            "count_messages": 0,  # Initialize count of messages
            "created_at": room.created_at,
            "secret_room": room.secret_room,
            "favorite": tab_info.favorite,
            "block": room.block
        }

        # Append room info to the list
        room_details.append(room_info)

    # Optionally, sort rooms by a specific criterion
    room_details.sort(key=lambda x: x['favorite'], reverse=True)

    return room_details



@router.post('/add-room-to-tab/{tab_id}/{room_id}')
async def add_room_to_tab(tab_id: int, room_id: int, 
                          db: Session = Depends(get_db), 
                          current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Add a room to a tab, remove from other if exists.

    Args:
        tab_id (int): The ID of the tab to add the room to.
        room_id (int): The ID of the room to add.
        db (Session): The database session.
        current_user (models.User): The currently authenticated user.

    Returns:
        dict: Confirmation of the room added to the tab.

    Raises:
        HTTPException: If the room or tab does not exist, or if the room is already in the specified tab.
    """
    
    # Check if the tab exists and belongs to the current user
    tab = db.query(models.RoomTabsInfo).filter(models.RoomTabsInfo.id == tab_id, 
                                               models.RoomTabsInfo.owner_id == current_user.id).first()
    if not tab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")

    # Check if the room exists
    room = db.query(models.Rooms).filter(models.Rooms.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    # Check if the room is already in the specified tab
    existing_link = db.query(models.RoomsTabs).filter(models.RoomsTabs.room_id == room_id,
                                                      models.RoomsTabs.tab_id == tab_id).first()
    if existing_link:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room already in this tab")

    # Remove the room from any other tab
    db.query(models.RoomsTabs).filter(models.RoomsTabs.room_id == room_id).delete()

    # Add the room to the tab
    new_room_tab = models.RoomsTabs(room_id=room_id, tab_id=tab_id, user_id=current_user.id, tab_name=tab.name_tab)
    db.add(new_room_tab)
    db.commit()

    return {"message": f"Room {room_id} added to tab {tab_id}"}



@router.put('/', status_code=status.HTTP_200_OK)
async def update_tab(id: int, update: room_schema.TabUpdate,
                     db: Session = Depends(get_db), 
                     current_user: models.User = Depends(oauth2.get_current_user)):
    
    tab = db.query(models.RoomTabsInfo).filter(models.RoomTabsInfo.id == id,
                                               models.RoomTabsInfo.owner_id == current_user.id).first()
    if not tab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")
    
        # Update fields if provided in the request
    if update.name_tab is not None:
        tab.name_tab = update.name_tab
    if update.image_tab is not None:
        tab.image_tab = update.image_tab
    db.commit()
    return {"message": "Tab updated successfully"}
    



@router.delete('/')
async def deleted_tab(id: int,
                      db: Session = Depends(get_db), 
                      current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Delete a tab.

    Args:
        id (int): The ID of the tab to delete.
        db (Session): The database session.
        current_user (models.User): The currently authenticated user.

    Raises:
        HTTPException: If the tab does not exist or the user does not have sufficient permissions.

    Returns:
        Response: An empty response with status code 204 if the tab was deleted successfully.
    """
    
    tab = db.query(models.RoomTabsInfo).filter(models.RoomTabsInfo.id == id,
                                               models.RoomTabsInfo.owner_id == current_user.id).first()
    if not tab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")
    
    db.delete(tab)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    
    
    
    




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
