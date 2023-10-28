from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.database import get_async_session, async_session_maker
from app import models, schemas
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, insert
from typing import List

router = APIRouter(
    prefix="/chat",
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
        await websocket.send_text(message)

    async def broadcast(self, message: str, add_to_db: bool):
        if add_to_db:
            await self.add_messages_to_database(message)
        for connection in self.active_connections:
            await connection.send_text(message)

    @staticmethod
    async def add_messages_to_database(message: str):
        async with async_session_maker() as session:
            stmt = insert(models.Socket).values(message=message, rooms="Holl", receiver_id=3)
            await session.execute(stmt)
            await session.commit()
            
            
manager = ConnectionManager()





async def fetch_last_messages(session: AsyncSession) -> List[schemas.SocketModel]:
    query = select(models.Socket).order_by(desc(models.Socket.id)).limit(5)
    result = await session.execute(query)
    messages = result.scalars().all()
    return messages

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, session: AsyncSession = Depends(get_async_session)):
    await manager.connect(websocket)
    
    # Отримуємо останні повідомлення
    messages = await fetch_last_messages(session)

    # Відправляємо кожне повідомлення користувачеві
    for message in messages:
        await websocket.send_text(f"Previous message: {message.message}")  # або яке поле ви хочете використовувати
    
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}", add_to_db=True)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat", add_to_db=False)
