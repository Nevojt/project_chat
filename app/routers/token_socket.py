from fastapi import WebSocket, Depends, APIRouter, status, HTTPException
from fastapi.websockets import WebSocketState, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, asc
from app.database import get_db
from app import models, schemas, oauth2
from datetime import datetime
import json
from typing import List, Optional

router = APIRouter()

active_websockets = {}

@router.websocket("/ws/{rooms}")
async def websocket_endpoint(websocket: WebSocket, rooms: str, token: str = None, db: Session = Depends(get_db)):
    
    user = None
    try:
        if token is None:
            await websocket.close(code=1008)  # Close the WebSocket connection if token is missing
            return

        user = oauth2.get_current_user(token, db)

        if user is None:
            await websocket.close(code=1008)  # Close the WebSocket connection if the token is invalid
            return

        await websocket.accept()
        active_websockets[user.user_name] = websocket
        await websocket.send_text(f"Welcome, {user.user_name}!")

        messages = await get_messages(db, rooms)
        serialized_messages = []

        for message in messages:
            message_dict = row_to_dict(message)
            serialized_messages.append(message_dict)
        
        await websocket.send_text(json.dumps(serialized_messages, ensure_ascii=False))

        while True:
            data = await websocket.receive_text()
            message_data = schemas.MessageCreate.model_validate_json(data)
            serialized_message = await create_message(message_data, user, db)
            for ws in active_websockets.values():
                await ws.send_text(json.dumps(serialized_message, ensure_ascii=False))

    except WebSocketDisconnect:
        if user and user.user_name in active_websockets:
            del active_websockets[user.user_name]
    except Exception as e:
        await websocket.send_text(f"An error occurred: {str(e)}")
        if user and user.user_name in active_websockets:
            del active_websockets[user.user_name]
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()

        
         
        
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

            result_data["message"] = message_data  # Додайте дані повідомлення до нового словника
        else:
            result_data[key] = value  # Збережіть інші дані без змін

    return result_data






async def create_message(post: schemas.MessageCreate, current_user: models.User, db: Session = Depends(get_db)):
    message = models.Message(owner_id=current_user.id, **post.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)
 
    serialized_message = row_to_dict(message)  # Серіалізуємо повідомлення
    
    return serialized_message  # Повертаємо серіалізоване повідомлення
