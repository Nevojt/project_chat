from fastapi import WebSocket, Depends, APIRouter
from fastapi.websockets import WebSocketState, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app import models, schemas, oauth2
from datetime import datetime
import json


router = APIRouter()



@router.websocket("/ws/ws/{rooms}")
async def socket_new(websocket: WebSocket, rooms: str, db: Session = Depends(get_db)):
    while True:
        data = await websocket.receive_text()
        message_data = schemas.MessageCreate.model_validate_json(data)
        await create_message(message_data, db)






async def create_message(post: schemas.MessageCreate, current_user: models.User, db: Session = Depends(get_db)):
    message = models.Message(owner_id=current_user.id, **post.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)
 
    return message