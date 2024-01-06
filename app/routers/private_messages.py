import logging
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
router = APIRouter(
    prefix="/direct",
    tags=['Direct'],
)

logging.basicConfig(filename='log/private.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# @router.get("/")
# async def get_all_private_messages(db: Session = Depends(get_db)):
#     query = db.query(models.PrivateMessage).all()
#     return query


@router.get("/{user_id}", response_model=List[schemas.PrivateInfoRecipient])
async def get_private_recipient(user_id: int, db: Session = Depends(get_db)):
    # Query for recipients and senders
    messages_query = db.query(models.PrivateMessage, models.User).join(
        models.User, models.PrivateMessage.recipient_id == models.User.id
    ).filter(
        (models.PrivateMessage.sender_id == user_id) | (models.PrivateMessage.recipient_id == user_id)
    )

    # Execute query
    messages = messages_query.all()

    # Filter and map results
    read_users = {}
    unread_users = {}
    for message, user in messages:
        if message.recipient_id == user_id and not message.is_read:
            continue  # Skip unread messages where the user is the recipient

        other_user_id = message.sender_id if message.recipient_id == user_id else message.recipient_id
        other_user = db.query(models.User).filter(models.User.id == other_user_id).first()

        target_dict = read_users if message.is_read and message.recipient_id == user_id else unread_users
        if other_user_id not in target_dict:
            target_dict[other_user_id] = schemas.PrivateInfoRecipient(
                recipient_id=other_user_id,
                recipient_name=other_user.user_name,
                recipient_avatar=other_user.avatar,
                verified=other_user.verified,
                is_read=message.is_read if message.recipient_id == user_id else False
            )

    # Combine and sort results
    result = list(read_users.values()) + list(unread_users.values())

    if not result:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Sorry, no recipients or senders found.")
    return result









# @router.get('/is_read/{user_id}')    
# async def check_is_read_messages(user_id: int, session: AsyncSession = Depends(get_async_session)) -> bool:
    # """
    # Перевіряє, чи є у користувача непрочитані повідомлення.

    # Args:
    #     user_id (int): ID користувача.

    # Returns:
    #     bool: True, якщо є непрочитані повідомлення, інакше False.
    # """
    # query = select(models.PrivateMessage).where(
    #     models.PrivateMessage.recipient_id == user_id,
    #     models.PrivateMessage.is_read == False
    # )
    # result = await session.execute(query)
    # return result.scalar() is not None