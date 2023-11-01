from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.connection_manager import ConnectionManager
from app.database import get_async_session
from app import models, schemas, oauth2
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc
from typing import List

router = APIRouter()


            
manager = ConnectionManager()






async def fetch_last_private_messages(session: AsyncSession, recipient_id: int) -> List[schemas.PrivateMessage]:
    query = select(models.PrivateMessage, models.User).join(
        models.User, models.PrivateMessage.sender_id == models.User.id
    ).where(
        models.PrivateMessage.recipient_id == recipient_id
    ).order_by(desc(models.PrivateMessage.id)).limit(5)

    result = await session.execute(query)
    raw_messages = result.all()

    messages = [
        schemas.PrivateMessage(
            created_at=private.created_at,
            recipient_id=private.recipient_id,
            sender_id=private.sender_id,
            messages=private.messages,
            user_name=user.user_name,
            avatar=user.avatar
                # Ensure messages attribute is passed
        )
        for private, user in raw_messages
    ]

    return messages



@router.websocket("/ws/private/{recipient_id}")
async def private_webprivate_endpoint(
    websocket: WebSocket,
    recipient_id: int,
    token: str,
    session: AsyncSession = Depends(get_async_session)
):
    user = await oauth2.get_current_user(token, session)

    await manager.connect(websocket, user.id, user.user_name, user.avatar)
    messages = await fetch_last_private_messages(session, recipient_id)

    for message in messages:  
        await websocket.send_text(message.model_dump_json())  # Use json() instead of model_dump_json()
        print(message.model_dump_json())

    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_private_message(data['messages'],
                                               sender_id=user.id,
                                               recipient_id=recipient_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)

