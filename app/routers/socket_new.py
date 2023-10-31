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

    async def broadcast(self, message: str, rooms: str, receiver_id: int, add_to_db: bool):
        message_data = {
            "receiver_id": receiver_id,
            "message": message
            
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
    query = select(models.Socket).order_by(desc(models.Socket.id)).limit(5)
    result = await session.execute(query)
    messages = result.scalars().all()
    return messages




@router.websocket("/ws/{rooms}")
async def websocket_endpoint(
    websocket: WebSocket,
    rooms: str,
    token: str,
    session: AsyncSession = Depends(get_async_session)
    ):
    
    user = await oauth2.get_current_user(token, session)
    print(user.user_name)
    user_id = user.id
    
    await manager.connect(websocket)
    
    # Отримуємо останні повідомлення
    messages = await fetch_last_messages(session)

    # Відправляємо кожне повідомлення користувачеві
    for message in messages:
        await websocket.send_json({message.receiver_id: message.message}) 
    
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(f"{data['message']}", rooms=rooms, receiver_id=user_id, add_to_db=True)

            
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{user.user_name} left the chat", rooms=rooms, receiver_id=user_id, add_to_db=False)

# new socket connection