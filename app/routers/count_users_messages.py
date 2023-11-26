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
async def get_posts(db: Session = Depends(get_db)):
    counts = db.query(models.Socket.rooms, func.count(models.Socket.id).label('count')).group_by(models.Socket.rooms).all()
    if not counts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No messages found in any room.")
    return counts
