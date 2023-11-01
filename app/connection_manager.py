from datetime import datetime
import json
from fastapi import WebSocket
from app.database import async_session_maker
from app import models
from sqlalchemy import insert
from typing import List, Dict, Tuple








class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, Tuple[WebSocket, str, str]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, user_name: str, avatar: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = (websocket, user_name, avatar)

    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections.remove(websocket)
        self.user_connections.pop(user_id, None)
        
    async def send_private_message(self, message: str, sender_id: int, recipient_id: int):
        if sender_id in self.user_connections and recipient_id in self.user_connections:
            sender_websocket, sender_name, sender_avatar = self.user_connections[sender_id]
            recipient_websocket, _, _ = self.user_connections[recipient_id]

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message_data = {
                "created_at": current_time,
                "sender_id": sender_id,
                "message": message,
                "user_name": sender_name,
                "avatar": sender_avatar,
            }
            
            message_json = json.dumps(message_data, ensure_ascii=False)
            
            await sender_websocket.send_text(message_json)
            await recipient_websocket.send_text(message_json)

            # Зберігаємо повідомлення в базі даних
            await self.add_private_message_to_database(message, sender_id, recipient_id)

    async def broadcast(self, message: str, rooms: str, receiver_id: int, user_name: str, avatar: str, created_at: str, add_to_db: bool):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_data = {
            "created_at": current_time,
            "receiver_id": receiver_id,
            "message": message,
            "user_name": user_name,
            "avatar": avatar,         
        }
        
        message_json = json.dumps(message_data, ensure_ascii=False)
        
        if add_to_db:
            await self.add_messages_to_database(message, rooms, receiver_id)
            
        for connection in self.active_connections:
            await connection.send_text(message_json)

    @staticmethod
    async def add_messages_to_database(message: str, rooms: str, receiver_id: int):
        async with async_session_maker() as session:
            stmt = insert(models.Socket).values(message=message, rooms=rooms, receiver_id=receiver_id)
            await session.execute(stmt)
            await session.commit()
            
    @staticmethod
    async def add_private_message_to_database(message: str, sender_id: int, recipient_id: int):
        async with async_session_maker() as session:
            stmt = insert(models.PrivateMessage).values(messages=message, sender_id=sender_id, recipient_id=recipient_id)
            await session.execute(stmt)
            await session.commit()
     
            
    async def send_active_users(self):
        active_users = [{"user_id": user_id, "user_name": user_info[1], "avatar": user_info[2]} for user_id, user_info in self.user_connections.items()]
        message_data = {"type": "active_users", "data": active_users}
        for websocket, _, _ in self.user_connections.values():
            await websocket.send_json(message_data)