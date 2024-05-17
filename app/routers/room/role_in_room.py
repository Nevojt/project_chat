from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.database.async_db import get_async_session
from app.auth import oauth2
from app.models import models


router = APIRouter(
    prefix="/role-in-room",
    tags=['Role In Rooms']
)


@router.get('/')
async def list_role_in_room(db: AsyncSession = Depends(get_async_session), 
                          current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Retrieves the role in room for the authenticated user.

    Parameters:
    db (AsyncSession): The database session for asynchronous operations.
    current_user (models.User): The current user making the request.

    Returns:
    List[models.RoleInRoom]: A list of RoleInRoom objects for the specified user.

    Raises:
    HTTPException: If the user with the given ID is not found in the database.
    """
    role_query = select(models.RoleInRoom).where(models.RoleInRoom.user_id == current_user.id)
    result = await db.execute(role_query)
    role_in_room = result.scalars().all()
    
    if not role_in_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with ID: {current_user.id} not found")
        
    return role_in_room

# Get info user role admin option
@router.get('/admin/{user_id}')
async def list_role_in_room(user_id: int, db: AsyncSession = Depends(get_async_session), 
                          current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Admin option to get role in room for a specific user.

    Parameters:
    user_id (int): The ID of the user whose role in room needs to be fetched.
    db (AsyncSession): The database session for asynchronous operations.
    current_user (models.User): The current user making the request.

    Returns:
    List[models.RoleInRoom]: A list of RoleInRoom objects for the specified user.

    Raises:
    HTTPException: If the user with the given ID is not found in the database.
    HTTPException: If the current user is not an admin.
    """
    
    role_query = select(models.RoleInRoom).where(models.RoleInRoom.user_id == user_id)
    result = await db.execute(role_query)
    role_in_room = result.scalars().all()
    
    if not role_in_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with ID: {user_id} not found")
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
    return role_in_room

@router.post('/to_moderator/{user_id}')
async def to_moderator(user_id: int, room_id:int, db: AsyncSession = Depends(get_async_session), 
                          current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Endpoint to toggle a user's role from moderator to regular user or vice versa in a specific room.
    Only the room owner can perform this action.

    Parameters:
    user_id (int): The ID of the user whose role needs to be toggled.
    room_id (int): The ID of the room where the role needs to be toggled.
    db (AsyncSession): The database session for asynchronous operations.
    current_user (models.User): The current user making the request.

    Returns:
    dict: A dictionary with a success message indicating the role change.

    Raises:
    HTTPException: If the current user is not the owner of the room.
    """

    # Check if the current user is the owner of the room
    room_owner_query = select(models.Rooms).where(models.Rooms.owner == current_user.id,
                                                  models.Rooms.id == room_id)
    result = await db.execute(room_owner_query)
    room_owner = result.scalar_one_or_none()
    
    user_verification = select(models.User).where(models.User.id == user_id)
    result = await db.execute(user_verification)
    user_verification = result.scalar_one_or_none()
    
    if user_verification.verified is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with ID: {user_id} not verification")

    if room_owner is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this room.")

    # Request to check the existing user role in the room
    role_query = select(models.RoleInRoom).where(models.RoleInRoom.user_id == user_id,
                                                 models.RoleInRoom.room_id == room_id)
    result = await db.execute(role_query)
    role_in_room = result.scalar_one_or_none()
   
    if role_in_room is None:
        # If the role does not exist, add the user as a moderator
        add_role_moderator = models.RoleInRoom(user_id=user_id, room_id=room_id, role="moderator")
        db.add(add_role_moderator)
        await db.commit()
        return {"msg": f"User with ID: {user_id} is now a moderator in room with ID: {room_id}"}
    else:
        # If the role exists, delete it
        await db.delete(role_in_room)
        await db.commit()
        return {"msg": f"User with ID: {user_id} is no longer a moderator in room with ID: {room_id}"}
    