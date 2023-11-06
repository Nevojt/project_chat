from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.connection_manager import ConnectionManager
from app.database import get_async_session
from app import models, schemas, oauth2
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, asc
from typing import List

router = APIRouter(
    tags=["Chat"]
)


            
manager = ConnectionManager()


async def fetch_last_messages(rooms:str, session: AsyncSession) -> List[schemas.SocketModel]:
    query = select(models.Socket, models.User).filter(models.Socket.rooms == rooms).join(
        models.User, models.Socket.receiver_id == models.User.id
    ).order_by(asc(models.Socket.created_at)).limit(50)

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
    messages = await fetch_last_messages(rooms, session)

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