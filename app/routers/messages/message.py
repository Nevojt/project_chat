from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.auth import oauth2
from app.database.async_db import get_async_session
from app.models import models
from app.schemas import message
from app.config.config import settings
from sqlalchemy.future import select
from typing import List

import base64
from cryptography.fernet import Fernet, InvalidToken

router = APIRouter(
    prefix="/messages",
    tags=['Message'],
)





key = settings.key_crypto
cipher = Fernet(key)

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode('utf-8') == s
    except Exception:
        return False


async def async_decrypt(encoded_data: str):
    if not is_base64(encoded_data):
       
        return encoded_data  

    try:
        encrypted = base64.b64decode(encoded_data.encode('utf-8'))
        decrypted = cipher.decrypt(encrypted).decode('utf-8')
        return decrypted
    except InvalidToken:
        return None

@router.get("/", response_model=List[message.SocketModel], include_in_schema=False)
async def get_posts(session: AsyncSession = Depends(get_async_session), 
                    limit: int = 50, skip: int = 0):
    
    """
    Retrieves a list of socket messages with associated user details, paginated by a limit and offset.

    Args:
        session (AsyncSession, optional): Asynchronous database session. Defaults to Depends(get_async_session).
        limit (int, optional): Maximum number of messages to retrieve. Defaults to 50.
        skip (int, optional): Number of messages to skip for pagination. Defaults to 0.

    Returns:
        List[schemas.SocketModel]: A list of socket messages along with user details, structured as per SocketModel schema.
    """

    query = select(
        models.Socket, 
        models.User, 
        func.coalesce(func.sum(models.Vote.dir), 0).label('votes')
    ).outerjoin(
        models.Vote, models.Socket.id == models.Vote.message_id
    ).join(
        models.User, models.Socket.receiver_id == models.User.id
    ).group_by(
        models.Socket.id, models.User.id
    ).order_by(
        desc(models.Socket.created_at)
    ).limit(50)

    result = await session.execute(query)
    raw_messages = result.all()

    result = await session.execute(query)
    raw_messages = result.all()

    # Convert raw messages to SocketModel
    messages = []
    for socket, user, votes in raw_messages:
        decrypted_message = await async_decrypt(socket.message)
        messages.append(
            message.SocketModel(
                created_at=socket.created_at,
                receiver_id=socket.receiver_id,
                message=decrypted_message,
                fileUrl=socket.fileUrl,
                user_name=user.user_name if user is not None else "Unknown user",
                avatar=user.avatar if user is not None else "https://example.com/default_avatar.webp",
                verified=user.verified if user is not None else None,
                id=socket.id,
                vote=votes,
                id_return=socket.id_return,
                edited=socket.edited
            )
        )
    messages.reverse()
    return messages

async def check_room_blocked(room_id: int, session: AsyncSession):
    query = select(models.Rooms).where(models.Rooms.id == room_id, models.Rooms.block.is_(True))
    try:
        result = await session.execute(query)
        room_record = result.scalar_one()
        return True
    except NoResultFound:
        return False

@router.get("/{room_id}", response_model=List[message.SocketModel])
async def get_messages_room(room_id: int, 
                            session: AsyncSession = Depends(get_async_session), 
                            limit: int = 50, skip: int = 0):
    """
    Retrieves a list of socket messages with associated user details, paginated by a limit and offset.

    Args:
        rooms (str): The rooms of the message.
        session (AsyncSession, optional): Asynchronous database session. Defaults to Depends(get_async_session).
        limit (int, optional): Maximum number of messages to retrieve. Defaults to 50.
        skip (int, optional): Number of messages to skip for pagination. Defaults to 0.

    Returns:
        List[schemas.SocketModel]: A list of socket messages along with user details, structured as per SocketModel schema.
    """
    room_blocked = await check_room_blocked(room_id, session)  
    if room_blocked:
        raise HTTPException(status_code=403, detail="Room is blocked")
    
    room = select(models.Rooms).where(models.Rooms.id == room_id)
    result = await session.execute(room)
    existing_room = result.scalar_one_or_none()
    if existing_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    
    query = select(
    models.Socket, 
    models.User, 
    func.coalesce(func.sum(models.Vote.dir), 0).label('votes')
    ).outerjoin(
        models.Vote, models.Socket.id == models.Vote.message_id
    ).outerjoin( 
        models.User, models.Socket.receiver_id == models.User.id
    ).filter(
        models.Socket.rooms == existing_room.name_room
    ).group_by(
        models.Socket.id, models.User.id
    ).order_by(
        desc(models.Socket.created_at)
    )

    result = await session.execute(query)
    raw_messages = result.all()

    # Convert raw messages to SocketModel
    messages = []
    for socket, user, votes in raw_messages:
        decrypted_message = await async_decrypt(socket.message)
        messages.append(
            message.SocketModel(
                created_at=socket.created_at,
                receiver_id=socket.receiver_id,
                message=decrypted_message,
                fileUrl=socket.fileUrl,
                user_name=user.user_name if user is not None else "Unknown user",
                avatar=user.avatar if user is not None else "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/photo_2024-06-14_19-20-40.jpg",
                verified=user.verified if user is not None else None,
                id=socket.id,
                vote=votes,
                id_return=socket.id_return,
                edited=socket.edited
            )
        )
    messages.reverse()
    return messages




@router.put("/{id}", include_in_schema=False)
async def change_message(id_message: int, message_update: message.SocketUpdate,
                         current_user: models.User = Depends(oauth2.get_current_user), 
                         session: AsyncSession = Depends(get_async_session)):
    
    
    query = select(models.Socket).where(models.Socket.id == id_message, models.Socket.receiver_id == current_user.id)
    result = await session.execute(query)
    message = result.scalar()

    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found or you don't have permission to edit this message")

    message.message = message_update.message
    session.add(message)
    await session.commit()

    return {"message": "Message updated successfully"}
    

        