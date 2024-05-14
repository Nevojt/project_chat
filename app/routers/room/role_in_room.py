from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.database.async_db import get_async_session
from app.auth import oauth2
from app.models import models


router = APIRouter(
    prefix="/role-in-room",
    tags=['Role Im Rooms']
)

# Get info role current user
@router.get('/')
async def list_role_in_room(db: AsyncSession = Depends(get_async_session), 
                          current_user: models.User = Depends(oauth2.get_current_user)):
    
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
    """Admin option"""
    
    role_query = select(models.RoleInRoom).where(models.RoleInRoom.user_id == user_id)
    result = await db.execute(role_query)
    role_in_room = result.scalars().all()
    
    if not role_in_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with ID: {user_id} not found")
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
    return role_in_room