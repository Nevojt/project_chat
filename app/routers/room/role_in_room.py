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

