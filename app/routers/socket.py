from fastapi import WebSocket, Depends, APIRouter
from fastapi.websockets import WebSocketState, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app import models, schemas, oauth2
from datetime import datetime
import json


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
        
        if rooms not in active_websockets:
            active_websockets[rooms] = {}
        active_websockets[rooms][user.id, user.user_name, user.avatar] = websocket

        messages = await get_messages(db, rooms)
        serialized_messages = []

        for message in messages:
            message_dict = row_to_dict(message)
            serialized_messages.append(message_dict)
        
        await websocket.send_text(json.dumps(serialized_messages, ensure_ascii=False))

        while True:
            data = await websocket.receive_text()
            message_data = schemas.MessageCreate.model_validate_json(data)
            await create_message(message_data, user, db)
            
            one_message = await get_latest_message(db, rooms)

            users_to_remove = []

            for username, ws in list(active_websockets[rooms].items()):
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_text(json.dumps(one_message, ensure_ascii=False))
                else:
                    users_to_remove.append(username)

            # Видалення користувачів після завершення ітерації
            for username in users_to_remove:
                active_websockets[rooms].pop(username)


    except WebSocketDisconnect:
        if user and rooms in active_websockets:
            key_to_remove = (user.id, user.user_name, user.avatar)
            if key_to_remove in active_websockets[rooms]:
                active_websockets[rooms].pop(key_to_remove)

                
    # except Exception as e:
    #     await websocket.send_text(f"An error occurred: {str(e)}")
    #     if user and user.id in active_websockets:
    #         del active_websockets[user.id]
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
            
            
@router.get("/ws/users/{rooms}")
async def get_users_in_room(rooms: str):
    if rooms in active_websockets:
        users = list(active_websockets[rooms].keys())
        return {"users": users}
    else:
        return {"users": []}
      
        
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

async def get_latest_message(db: Session = Depends(get_db), rooms: str = None):
    latest_message = db.query(models.Message).filter(models.Message.rooms == rooms).order_by(desc(models.Message.id)).first()
    if latest_message:
        return {
            "message": {
                "id": latest_message.id,
                "owner_id": latest_message.owner_id,
                "message": latest_message.message,
                "created_at": latest_message.created_at.isoformat(),
                "rooms": latest_message.rooms,
                "is_privat": latest_message.is_privat,
                "receiver_id": latest_message.receiver_id,
                "owner": {
                    "id": latest_message.owner.id,
                    "user_name": latest_message.owner.user_name,
                    "avatar": latest_message.owner.avatar,
                    "created_at": latest_message.owner.created_at.isoformat()
                },
                "receiver": {
                    "id": latest_message.receiver.id,
                    "user_name": latest_message.receiver.user_name,
                    "avatar": latest_message.receiver.avatar,
                    "created_at": latest_message.receiver.created_at.isoformat()
                }
            },
            "votes": 0  # Ваш код для отримання голосів тут
        }
    else:
        return None  # Якщо немає останнього повідомлення


async def create_message(post: schemas.MessageCreate, current_user: models.User, db: Session = Depends(get_db)):
    message = models.Message(owner_id=current_user.id, **post.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)
 
    serialized_message = row_to_dict(message)  # Серіалізуємо повідомлення
    return serialized_message  # Повертаємо серіалізоване повідомлення

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



def remove_user_from_active(rooms, username):
    if rooms in active_websockets and username in active_websockets[rooms]:
        del active_websockets[rooms][username]
     



