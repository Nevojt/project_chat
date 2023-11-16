from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session, aliased
from sqlalchemy import or_
from typing import List
from ..database import get_db
from .. import models, schemas
router = APIRouter(
    prefix="/direct",
    tags=['Direct'],
)


@router.get("/")
async def get_all_private_messages(db: Session = Depends(get_db)):
    query = db.query(models.PrivateMessage).all()
    return query


@router.get("/{user_id}", response_model=List[schemas.PrivateInfoRecipient])
async def get_private_recipient(sender_id: int, db: Session = Depends(get_db)):
    query = db.query(models.PrivateMessage, models.User).distinct(models.PrivateMessage.recipient_id).join(
        models.User, models.PrivateMessage.recipient_id == models.User.id
    ).filter(
        models.PrivateMessage.sender_id == sender_id
    ).all()
    
    result = [
        schemas.PrivateInfoRecipient(
            recipient_id=message.recipient_id,
            recipient_name=user.user_name,
            recipient_avatar=user.avatar)
        for message, user in query
    ]
    if not result:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Sorry not recipients")
    return result



# @router.get("/{user_id}", response_model=List[schemas.PrivateRecipient])
# async def get_private_messages(user_id: int, db: Session = Depends(get_db)):
    
    sender_alias = aliased(models.User)
    recipient_alias = aliased(models.User)

    query = db.query(models.PrivateMessage, sender_alias, recipient_alias).join(
        sender_alias, models.PrivateMessage.sender_id == sender_alias.id
    ).join(
        recipient_alias, models.PrivateMessage.recipient_id == recipient_alias.id
    ).filter(
        or_(
            models.PrivateMessage.sender_id == user_id,
            models.PrivateMessage.recipient_id == user_id
        )
    ).all()
    
    results = [
            schemas.PrivateRecipient(
            sender_id=message.sender_id,
            sender_name=sender.user_name,
            sender_avatar=sender.avatar,
            recipient_id=message.recipient_id,
            recipient_name=recipient.user_name,
            recipient_avatar=recipient.avatar
        )
        for message, sender, recipient in query
        ]
    
        
    return results
