
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.connection_manager import ConnectionManagerPrivate
from app.database import get_async_session
from app import models, oauth2
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, asc, or_
from typing import List

router = APIRouter()


            
manager = ConnectionManagerPrivate()



async def fetch_last_private_messages(session: AsyncSession, sender_id: int, recipient_id: int) -> List[dict]:
    
    """
    Fetch the last private messages between two users from the database.

    Args:
    session (AsyncSession): The database session to execute the query.
    sender_id (int): The ID of the user who sent the message.
    recipient_id (int): The ID of the user who received the message.

    Returns:
    List[dict]: A list of dictionaries containing message details.
    """
    
    query = select(models.PrivateMessage, models.User).join(
        models.User, models.PrivateMessage.sender_id == models.User.id
    ).where(
        or_(
            and_(models.PrivateMessage.sender_id == sender_id, models.PrivateMessage.recipient_id == recipient_id),
            and_(models.PrivateMessage.sender_id == recipient_id, models.PrivateMessage.recipient_id == sender_id)
        )
    ).order_by(asc(models.PrivateMessage.id))#.limit(5)

    result = await session.execute(query)
    raw_messages = result.all()

    messages = [
        {
            "created_at": private.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "sender_id": private.sender_id,
            "message": private.messages,
            "user_name": user.user_name,
            "avatar": user.avatar,
        }
        for private, user in raw_messages
    ]

    return messages


async def unique_user_name_id(user_id: int, user_name: str):
    unique_user_name_id = f"{user_id}-{user_name}"

    
    return unique_user_name_id
    


@router.websocket("/ws/private/{recipient_id}")
async def web_private_endpoint(
    websocket: WebSocket,
    recipient_id: int,
    token: str,
    session: AsyncSession = Depends(get_async_session)
):
    
    """
    WebSocket endpoint for handling private messaging between users.

    Args:
    websocket (WebSocket): The WebSocket connection instance.
    recipient_id (int): The ID of the message recipient.
    token (str): The authentication token of the current user.
    session (AsyncSession): The database session, injected by dependency.

    Operations:
    - Authenticates the current user.
    - Establishes a WebSocket connection.
    - Fetches and sends the last private messages to the connected client.
    - Listens for incoming messages and handles sending and receiving of private messages.
    - Disconnects on WebSocket disconnect event.
    """
    
    
    user = await oauth2.get_current_user(token, session)
   
    await manager.connect(websocket, user.id, recipient_id)
    messages = await fetch_last_private_messages(session, user.id, recipient_id)

    for message in messages:  
        message_json = json.dumps(message, ensure_ascii=False)
        await websocket.send_text(message_json)

    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_private_message(data['messages'],
                                               sender_id=user.id,
                                               recipient_id=recipient_id,
                                               user_name=user.user_name,
                                               avatar=user.avatar
                                               )
    except WebSocketDisconnect:
        manager.disconnect(user.id, recipient_id)


