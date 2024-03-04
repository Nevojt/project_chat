from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import oauth2
from app.database.async_db import get_async_session
from app.model_schema import models, schemas
from sqlalchemy.future import select
from typing import List

router = APIRouter(
    prefix="/messages",
    tags=['Message'],
)


@router.get("/", response_model=List[schemas.SocketModel])
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
        schemas.SocketModel(
            created_at=socket.created_at,
            receiver_id=socket.receiver_id,
            id=socket.id,
            message=socket.message,
            user_name=user.user_name,
            avatar=user.avatar,
            verified=user.verified,
            vote=votes,
            id_return=socket.id_return,
        )
        for socket, user, votes in raw_messages
    ]

    return messages



@router.get("/{rooms}", response_model=List[schemas.SocketModel])
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
    ).join(
        models.User, models.Socket.receiver_id == models.User.id
    ).filter(
        models.Socket.rooms == rooms
    ).group_by(
        models.Socket.id, models.User.id
    ).order_by(
        desc(models.Socket.created_at)
    ).limit(50)

    result = await session.execute(query)
    raw_messages = result.all()

    # Convert raw messages to SocketModel
    messages = [
        schemas.SocketModel(
            created_at=socket.created_at,
            receiver_id=socket.receiver_id,
            message=socket.message,
            user_name=user.user_name,
            avatar=user.avatar,
            verified=user.verified,
            id=socket.id,
            vote=votes, # Додавання кількості голосів
            id_return=socket.id_return
        )
        for socket, user, votes in raw_messages
    ]
    messages.reverse()
    return messages









# @router.get("/{rooms}", response_model=List[schemas.MessageOut])
# async def get_post(rooms: str, db: Session = Depends(get_db),
#                    limit: int = 50, skip: int = 0, search: Optional[str] = ""):
    
    
#     post = db.query(models.Message, func.count(models.Vote.message_id).label("votes")).join(
#         models.Vote, models.Vote.message_id == models.Message.id, isouter=True).group_by(models.Message.id).filter(
#             models.Message.rooms == rooms, models.Message.message.contains(search)).order_by(
#                 asc(models.Message.created_at)).limit(limit).offset(skip).all()
#     if not post:  
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with rooms: {rooms} not found")
#     return post






# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.MessagePost)
# async def create_post(post: schemas.MessageCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    

#     post = models.Message(owner_id=current_user.id, **post.model_dump())
#     db.add(post)
#     db.commit()
#     db.refresh(post)    
#     return post


# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
#     post_query = db.query(models.Message).filter(models.Message.id == id)
    
#     post = post_query.first()
    
#     if post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} not found")
        
#     if post.owner_id != current_user.id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail=f"Not authorized to perform requested action")
    
#     post_query.delete(synchronize_session=False)
#     db.commit()
#     return Response(status_code=status.HTTP_204_NO_CONTENT)



# @router.put("/{id}", response_model=schemas.MessagePost)
# def update_post(id: int, update_post: schemas.MessageCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
#     post_query = db.query(models.Message).filter(models.Message.id == id)
#     post = post_query.first()
    
#     if post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} not found")
        
#     if post.owner_id != current_user.id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail=f"Not authorized to perform requested action")
    
#     post_query.update(update_post.model_dump(), synchronize_session=False)
    
#     db.commit()
#     return post_query.first()

@router.put("/{id}")
async def change_message(id_message: int, message_update: schemas.SocketUpdate,
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
    

        