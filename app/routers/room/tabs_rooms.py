from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
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
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")
        
    try:
        # Check if tab already exists
        post_tab = select(models.RoomTabsInfo).where(models.RoomTabsInfo.name_tab == tab.name_tab)
        result = await db.execute(post_tab)
        existing_room = result.scalar_one_or_none()

        if existing_room:
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                                detail=f"Tab {tab.name_tab} already exists")
            
        # Check the number of tabs the user already owns
        tab_count_query = select(func.count()).where(models.RoomTabsInfo.owner_id == current_user.id)
        tab_count = await db.scalar(tab_count_query)

        if tab_count >= 10:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Maximum tab limit reached. You can only have 10 tabs.")
        
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



@router.post('/add-room-to-tab/{tab_id}')
async def add_rooms_to_tab(tab_id: int, room_ids: List[int], 
                           db: Session = Depends(get_db), 
                           current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Add multiple rooms to a tab, remove them from other tabs if they exist.

    Args:
        tab_id (int): The ID of the tab to add the rooms to.
        room_ids (List[int]): A list of room IDs to add.
        db (Session): The database session.
        current_user (models.User): The currently authenticated user.

    Returns:
        dict: Confirmation of the rooms added to the tab.

    Raises:
        HTTPException: If the tab does not exist, any room does not exist, or if any room is already in the specified tab.
    """
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")

    # Check if the tab exists and belongs to the current user
    tab = db.query(models.RoomTabsInfo).filter(models.RoomTabsInfo.id == tab_id, 
                                               models.RoomTabsInfo.owner_id == current_user.id).first()
    if not tab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")

    # Process each room
    for room_id in room_ids:
        room = db.query(models.Rooms).filter(models.Rooms.id == room_id).first()
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {room_id} not found")

        existing_link = db.query(models.RoomsTabs).filter(models.RoomsTabs.room_id == room_id,
                                                          models.RoomsTabs.tab_id == tab_id).first()
        if existing_link:
            continue  # Skip if room is already in the tab

        # Remove the room from any other tab
        db.query(models.RoomsTabs).filter(models.RoomsTabs.room_id == room_id).delete()

        # Add the room to the tab
        new_room_tab = models.RoomsTabs(room_id=room_id, tab_id=tab_id, user_id=current_user.id, tab_name=tab.name_tab)
        db.add(new_room_tab)

    db.commit()

    return {"message": f"Rooms {room_ids} added to tab {tab_id}"}



@router.put('/', status_code=status.HTTP_200_OK)
async def update_tab(id: int, update: room_schema.TabUpdate,
                     db: Session = Depends(get_db), 
                     current_user: models.User = Depends(oauth2.get_current_user)):
    
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
        
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


@router.put('/{room_id}')
async def room_update_to_favorites(room_id: int,
                                favorite: bool,
                                db: Session = Depends(get_db), 
                                current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Updates the favorite status of a room in tab for a specific user.

    Args:
        room_id (int): The ID of the room to update.
        favorite (bool): The new favorite status for the room.
        db (Session): The database session.
        current_user (models.User): The currently authenticated user.

    Returns:
        dict: A dictionary containing the room ID and the updated favorite status.

    Raises:
        HTTPException: If the user is blocked or not verified, a 403 Forbidden error is raised.
        HTTPException: If the room is not found, a 404 Not Found error is raised.
    """
    if current_user.blocked == True or current_user.verified == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")

    # Fetch room
    room = db.query(models.Rooms).filter(models.Rooms.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    # Check if there is already a favorite record
    favorite_record = db.query(models.RoomsTabs).filter(
        models.RoomsTabs.room_id == room_id,
        models.RoomsTabs.user_id == current_user.id
    ).first()

    # Update if exists, else create a new record
    if favorite_record:
        favorite_record.favorite = favorite
    else:
        new_favorite = models.RoomsTabs(
            favorite=favorite
        )
        db.add(new_favorite)

    db.commit()
    return {"room_id": room_id, "favorite": favorite}
    



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
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
    tab = db.query(models.RoomTabsInfo).filter(models.RoomTabsInfo.id == id,
                                               models.RoomTabsInfo.owner_id == current_user.id).first()
    if not tab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")
    
    db.delete(tab)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    
@router.delete('/delete-room-in-tab/{tab_id}')
async def delete_room_from_tab(tab_id: int, room_ids: List[int],
                               db: Session = Depends(get_db), 
                               current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Remove rooms from a tab.

    Args:
        tab_id (int): The ID of the tab to remove rooms from.
        room_ids (List[int]): List of room IDs to remove.
        db (Session): The database session.
        current_user (models.User): The currently authenticated user.

    Returns:
        Response: HTTP status indicating the outcome.
    """

    # Check if the tab exists and belongs to the current user
    if not db.query(models.RoomTabsInfo).filter(models.RoomTabsInfo.id == tab_id, 
                                                models.RoomTabsInfo.owner_id == current_user.id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")

    # Remove specified rooms from the tab
    for room_id in room_ids:
        room_link = db.query(models.RoomsTabs).filter(models.RoomsTabs.room_id == room_id,
                                                      models.RoomsTabs.tab_id == tab_id).first()
        if not room_link:
            continue  # If room not found in the tab, skip it
        
        db.delete(room_link)

    db.commit()  # Commit all changes at once

    return Response(status_code=status.HTTP_204_NO_CONTENT)