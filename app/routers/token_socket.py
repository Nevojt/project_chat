from fastapi import WebSocket, Depends, APIRouter, status, HTTPException, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, asc
from app.database import get_db
from app import models, schemas, oauth2
from datetime import datetime
import json
from typing import List, Optional
  # Import your token verification function

router = APIRouter()



@router.websocket("/ws/{rooms}")

async def websocket_endpoint(websocket: WebSocket, rooms: str, token: str = None, db: Session = Depends(get_db)):
    if token is None:
        await websocket.close(code=1008)  # Close the WebSocket connection if token is missing

    user = oauth2.get_current_user(token, db)

    if user is None:
        await websocket.close(code=1008)  # Close the WebSocket connection if the token is invalid

    await websocket.accept()
    await websocket.send_text(f"Welcome, {user.user_name}!")
    
    messages = await get_messages(db, rooms)
    serialized_messages = [row_to_dict(message) for message in messages]
    await websocket.send_text(json.dumps(serialized_messages, ensure_ascii=False))


    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Received: {data}")
        
        try:
            message_data = schemas.MessageCreate.parse_raw(data)
            
        except WebSocketDisconnect:
            await websocket.close()
            
        except Exception as e:
            await websocket.send_text(f"Error parsing data: {str(e)}")
            continue 

        message = await create_message(message_data,  user, db)
        await websocket.send_text(f"Message saved with ID: {message.id}")
        
        
        
        
async def get_messages(db: Session = Depends(get_db), rooms: str = None):
    query = db.query(models.Message, func.count(models.Vote.message_id).label("votes")).filter(
            models.Message.rooms == rooms)

    if rooms is not None:
        query = query.join(models.Vote, models.Vote.message_id == models.Message.id, isouter=True)
        query = query.group_by(models.Message.id)
    
    query = query.order_by(models.Message.created_at)
    result = query.all()

    posts = [{"message": row[0], "votes": row[1]} for row in result]
    return posts


def row_to_dict(row) -> dict:
    if isinstance(row, dict):
        data = row.copy()
    else:
        data = {column.name: getattr(row, column.name) for column in row.__table__.columns}

    result_data = {}  # Створіть новий словник для збереження змінених даних

    for key, value in data.items():
        if isinstance(value, datetime):
            result_data[key] = value.isoformat()
        elif isinstance(value, models.Message):
            # Створіть словник з даними користувача
            owner_data = {
                "id": value.owner.id,
                "user_name": value.owner.user_name,
                "avatar": value.owner.avatar,
                "created_at": value.owner.created_at.isoformat()
            }

            receiver_data = {
                "id": value.receiver.id,
                "user_name": value.receiver.user_name,
                "avatar": value.receiver.avatar,
                "created_at": value.receiver.created_at.isoformat()
            }

            # Створіть словник з даними повідомлення
            message_data = {
                "id": value.id,
                "owner_id": value.owner_id,
                "message": value.message,
                "created_at": value.created_at.isoformat(),
                "rooms": value.rooms,
                "is_privat": value.is_privat,
                "receiver_id": value.receiver_id,
                "owner": owner_data,
                "receiver": receiver_data
            }

            result_data["Message"] = message_data  # Додайте дані повідомлення до нового словника
        else:
            result_data[key] = value  # Збережіть інші дані без змін

    return result_data






async def create_message(post: schemas.MessageCreate, current_user: models.User, db: Session = Depends(get_db)):
    
    post = models.Message(owner_id=current_user.id, **post.dict())
    db.add(post)
    db.commit()
    db.refresh(post)    
    return post