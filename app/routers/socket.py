from datetime import datetime
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.database import get_async_session, async_session_maker
from app import models, schemas, oauth2
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, insert
from typing import List

router = APIRouter(
    tags=["Chat"]
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

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
            await connection.send_json(message_json)

    @staticmethod
    async def add_messages_to_database(message: str, rooms: str, receiver_id: int):
        async with async_session_maker() as session:
            stmt = insert(models.Socket).values(message=message, rooms=rooms, receiver_id=receiver_id)
            await session.execute(stmt)
            await session.commit()
            
manager = ConnectionManager()


async def fetch_last_messages(session: AsyncSession) -> List[schemas.SocketModel]:
    query = select(models.Socket, models.User).join(
        models.User, models.Socket.receiver_id == models.User.id
    ).order_by(desc(models.Socket.id)).limit(5)

    result = await session.execute(query)
    raw_messages = result.all()

    # Convert raw messages to SocketModel
    messages = [
        schemas.SocketModel(
            created_at=socket.created_at,
            receiver_id=socket.receiver_id,
            message=socket.message,
            user_name=user.user_name,
            avatar=user.avatar
        )
        for socket, user in raw_messages
    ]

    return messages




@router.websocket("/ws/{rooms}")
async def websocket_endpoint(
    websocket: WebSocket,
    rooms: str,
    token: str,
    session: AsyncSession = Depends(get_async_session)
    ):
    
    user = await oauth2.get_current_user(token, session)

    await manager.connect(websocket)
    
    # Отримуємо останні повідомлення
    messages = await fetch_last_messages(session)

    # Відправляємо кожне повідомлення користувачеві
    for message in messages:  
        await websocket.send_json(message.model_dump_json()) 
    
    try:
        while True:
            data = await websocket.receive_json()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            await manager.broadcast(f"{data['message']}",
                                    rooms=rooms,
                                    created_at=current_time,
                                    receiver_id=user.id,
                                    user_name=user.user_name,
                                    avatar=user.avatar,
                                    add_to_db=True)

            
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await manager.broadcast(f"Client #{user.user_name} left the chat",
                                rooms=rooms,
                                created_at=current_time,
                                receiver_id=user.id,
                                user_name=user.user_name,
                                avatar=user.avatar,
                                add_to_db=False)
