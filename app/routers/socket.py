from datetime import datetime
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.database import get_async_session, async_session_maker
from app import models, schemas, oauth2
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, insert
from typing import List, Dict, Tuple

router = APIRouter(
    tags=["Chat"]
)

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
            await connection.send_text(message_json)

    @staticmethod
    async def add_messages_to_database(message: str, rooms: str, receiver_id: int):
        async with async_session_maker() as session:
            stmt = insert(models.Socket).values(message=message, rooms=rooms, receiver_id=receiver_id)
            await session.execute(stmt)
            await session.commit()
            
    async def send_active_users(self):
        active_users = [{"user_id": user_id, "user_name": user_info[1], "avatar": user_info[2]} for user_id, user_info in self.user_connections.items()]
        message_data = {"type": "active_users", "data": active_users}
        for websocket, _, _ in self.user_connections.values():
            await websocket.send_json(message_data)
            
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

    await manager.connect(websocket, user.id, user.user_name, user.avatar)
    await manager.send_active_users()
    
    # Отримуємо останні повідомлення
    messages = await fetch_last_messages(session)

    # Відправляємо кожне повідомлення користувачеві
    for message in messages:  
        await websocket.send_text(message.model_dump_json()) 
    
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
        manager.disconnect(websocket, user.id)
        await manager.send_active_users()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await manager.broadcast(f"Цей користувач -> {user.user_name} пішов з чату 🏃",
                                rooms=rooms,
                                created_at=current_time,
                                receiver_id=user.id,
                                user_name=user.user_name,
                                avatar=user.avatar,
                                add_to_db=False)


@router.get('/ws/{rooms}/users')
async def active_users(rooms: str):
    active_users = [{"user_id": user_id, "user_name": user_info[1], "avatar": user_info[2]} for user_id, user_info in manager.user_connections.items()]
    return {"rooms": rooms, "active_users": active_users}