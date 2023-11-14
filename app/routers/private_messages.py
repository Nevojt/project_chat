from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(
    prefix="/private",
    tags=['Private'],
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







# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.RoomPost)
# async def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    
#     existing_room = db.query(models.Rooms).filter(models.Rooms.name_room == room.name_room).first()
#     if existing_room:
#         raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
#                             detail=f"Room {existing_room.name_room} already exists")
    
#     room = models.Rooms(**room.model_dump())
#     db.add(room)
#     db.commit()
#     db.refresh(room)    
#     return room