
from fastapi import status, HTTPException, Depends, APIRouter, Response, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import asc, func
from app.database import get_db
from app import models, schemas, oauth2
from typing import List, Optional
from datetime import datetime
import json


router = APIRouter()


@router.websocket("/ws/{rooms}")
async def websocket_endpoint(websocket: WebSocket, rooms: str, db: Session = Depends(get_db)):
    await websocket.accept()
    
    messages = await get_messages(db, rooms)
    serialized_messages = [row_to_dict(message) for message in messages]
    await websocket.send_text(json.dumps(serialized_messages, ensure_ascii=False))

    
    while True:
        data = await websocket.receive_text()
        
        try:
            message_data = schemas.MessageBase.parse_raw(data)
            print(type(message_data))
            
        except WebSocketDisconnect:
            await websocket.close()
            
        except Exception as e:
            await websocket.send_text(f"Error parsing data: {str(e)}")
            continue 

        message = await create_message(message_data, db)
        await websocket.send_json(f"Message saved with ID: {message.id}")


async def get_messages(db: Session = Depends(get_db), rooms: str = None):
    query = db.query(models.Message)
    
    if rooms is not None:
        query = query.filter(models.Message.rooms == rooms)
    
    posts = query.all()  # Remove the .all() here
    return posts


def row_to_dict(row) -> dict:
    data =  {column.name: getattr(row, column.name) for column in row.__table__.columns}
    
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data



async def create_message(post: schemas.MessageCreate, db: Session = Depends(get_db)):
    

    post = models.Message(**post.dict())
    db.add(post)
    db.commit()
    db.refresh(post)    
    return post





