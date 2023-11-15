from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(
    prefix="/direct",
    tags=['Direct'],
)


@router.get("/")
async def get_all_private_messages(db: Session = Depends(get_db)):
    query = db.query(models.PrivateMessage).all()
    return query





@router.get("/{recipient_id}", response_model=List[schemas.PrivateRecipient])
async def get_private_messages(recipient_id: int, db: Session = Depends(get_db)):
    
    query = db.query(models.PrivateMessage, models.User).join(
        models.User, models.PrivateMessage.recipient_id == models.User.id
    ).filter(
        models.PrivateMessage.recipient_id == recipient_id
    ).all()
    
    
    
    results = [
            schemas.PrivateRecipient(
            id=message.id,
            recipient_id=message.recipient_id,
            user_name=user.user_name,
            avatar=user.avatar,
            messages=message.messages,
            created_at=message.created_at
        )
        for message, user in query
        ]
        
    return results
