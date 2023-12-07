from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_async_session
from .. import models, schemas
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

    query = select(models.Socket, models.User).join(
        models.User, models.Socket.receiver_id == models.User.id
    ).order_by(desc(models.Socket.id)).limit(limit).offset(skip)

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



@router.get("/{rooms}", response_model=List[schemas.SocketModel])
async def get_posts(rooms: str, session: AsyncSession = Depends(get_async_session), limit: int = 50, skip: int = 0):
   
    query = select(models.Socket, models.User).join(
        models.User, models.Socket.receiver_id == models.User.id
    ).filter(models.Socket.rooms == rooms).order_by(desc(models.Socket.id)).limit(limit).offset(skip)

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
    if not messages:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with rooms: {rooms} not found")

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