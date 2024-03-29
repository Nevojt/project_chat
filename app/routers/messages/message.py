from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import oauth2
from app.database.async_db import get_async_session
from app.models import models
from app.schemas import message
from sqlalchemy.future import select
from typing import List

router = APIRouter(
    prefix="/messages",
    tags=['Message'],
)


@router.get("/", response_model=List[message.SocketModel])
async def get_posts(session: AsyncSession = Depends(get_async_session), limit: int = 50, skip: int = 0):
    
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
    messages = [
        message.SocketModel(
            created_at=socket.created_at,
            receiver_id=socket.receiver_id,
            id=socket.id,
            message=socket.message,
            fileUrl=socket.fileUrl,
            user_name=user.user_name,
            avatar=user.avatar,
            verified=user.verified,
            vote=votes,
            id_return=socket.id_return,
        )
        for socket, user, votes in raw_messages
    ]

    return messages



@router.get("/{rooms}", response_model=List[message.SocketModel])
async def get_messages_room(rooms: str, session: AsyncSession = Depends(get_async_session), limit: int = 50, skip: int = 0):
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
    query = select(
    models.Socket, 
    models.User, 
    func.coalesce(func.sum(models.Vote.dir), 0).label('votes')
    ).outerjoin(
        models.Vote, models.Socket.id == models.Vote.message_id
    ).outerjoin(  # Змінено на outerjoin
        models.User, models.Socket.receiver_id == models.User.id
    ).filter(
        models.Socket.rooms == rooms
    ).group_by(
        models.Socket.id, models.User.id
    ).order_by(
        desc(models.Socket.created_at)
    )

    result = await session.execute(query)
    raw_messages = result.all()

    messages = [
        message.SocketModel(
            created_at=socket.created_at,
            receiver_id=socket.receiver_id,
            message=socket.message,
            user_name=user.user_name if user is not None else "DELETED",  # Додана перевірка на None
            avatar=user.avatar if user is not None else "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/boy_1.webp",
            verified=user.verified if user is not None else None,
            id=socket.id,
            vote=votes,
            id_return=socket.id_return
        )
        for socket, user, votes in raw_messages
    ]
    messages.reverse()
    return messages




@router.put("/{id}")
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
    

        