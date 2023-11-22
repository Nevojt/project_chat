from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
router = APIRouter(
    prefix="/direct",
    tags=['Direct'],
)


@router.get("/")
async def get_all_private_messages(db: Session = Depends(get_db)):
    query = db.query(models.PrivateMessage).all()
    return query


@router.get("/{sender_id}", response_model=List[schemas.PrivateInfoRecipient])
async def get_private_recipient(sender_id: int, db: Session = Depends(get_db)):
    query = db.query(models.PrivateMessage, models.User).distinct(models.PrivateMessage.recipient_id).join(
        models.User, models.PrivateMessage.recipient_id == models.User.id
    ).filter(
        models.PrivateMessage.sender_id == sender_id
    ).all()
    
    result = [
        schemas.PrivateInfoRecipient(
            recipient_id=message.recipient_id,
            recipient_name=user.user_name,
            recipient_avatar=user.avatar,
            is_read=message.is_read)
        for message, user in query
    ]
    if not result:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Sorry not recipients")
    return result




# @router.get('/is_read/{user_id}')    
# async def check_unread_messages(user_id: int, session: AsyncSession = Depends(get_async_session)) -> bool:
#     """
#     Перевіряє, чи є у користувача непрочитані повідомлення.

#     Args:
#         user_id (int): ID користувача.

#     Returns:
#         bool: True, якщо є непрочитані повідомлення, інакше False.
#     """
#     query = select(models.PrivateMessage).where(
#         models.PrivateMessage.recipient_id == user_id,
#         models.PrivateMessage.is_read == False
#     )
#     result = await session.execute(query)
#     return result.scalar() is not None