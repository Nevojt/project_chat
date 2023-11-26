from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/count",
    tags=['Count']
    )



@router.get("/messages", response_model=List[schemas.CountMessages])
async def get_count_messages(db: Session = Depends(get_db)):
    query_result = db.query(models.Socket.rooms, func.count(models.Socket.id).label('count')).group_by(models.Socket.rooms).all()
    
    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No messages found in any room.")
    counts = [{"rooms": rooms, "count": count} for rooms, count in query_result]

    return counts



@router.get("/users", response_model=List[schemas.CountUsers])
async def get_count_users(db: Session = Depends(get_db)):
    query_result = db.query(models.User_Status.name_room, func.count(models.User_Status.id).label('count')).group_by(models.User_Status.name_room).all()
    
    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No users found in any room.")
    counts = [{"rooms": name_room, "count": count} for name_room, count in query_result]
    
    return counts
