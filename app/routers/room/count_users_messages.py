from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import room

router = APIRouter(
    prefix="/count",
    tags=['Count']
    )



@router.get("/messages", response_model=List[room.CountMessages])
async def get_count_messages(db: Session = Depends(get_db)):
    """
    Get the count of messages in each room.

    Parameters:
        db (Session): The database session.

    Returns:
        List[schemas.CountMessages]: A list of count messages.

    Raises:
        HTTPException: If no messages found.
    """
    query_result = db.query(models.Socket.rooms, func.count(models.Socket.id).label('count')).group_by(
        models.Socket.rooms).filter(models.Socket.rooms != 'Hell').all()
    
    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No messages found in any room.")
    counts = [{"rooms": rooms, "count": count} for rooms, count in query_result]

    return counts



@router.get("/users", response_model=List[room.CountUsers])
async def get_count_users(db: Session = Depends(get_db)):
    """
    Get the count of users in each room.

    Parameters:
        db (Session): The database session.

    Returns:
        List[schemas.CountUsers]: A list of count users.

    Raises:
        HTTPException: If no users found.
    """
    query_result = db.query(models.User_Status.name_room, func.count(models.User_Status.id).label('count')).group_by(
        models.User_Status.name_room).filter(models.User_Status.name_room != 'Hell').all()
    
    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No users found in any room.")
    counts = [{"rooms": name_room, "count": count} for name_room, count in query_result]
    
    return counts
