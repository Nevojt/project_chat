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

logging.basicConfig(filename='_log/private.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@router.get("/{user_id}", response_model=List[schemas.PrivateInfoRecipient])
async def get_private_recipient(user_id: int, db: Session = Depends(get_db)):
    """
    Get a list of recipients in a private chat.

    Args:
        user_id (int): The ID of the user whose recipients you want to retrieve.
        db (Session): The database session.

    Returns:
        List[schemas.PrivateInfoRecipient]: A list of recipients in the private chat.

    Raises:
        HTTPException: If the user does not have any recipients or senders in the chat.
    """
    try:
        # Query for recipients and senders
        messages_query = db.query(models.PrivateMessage, models.User).join(
            models.User, models.PrivateMessage.recipient_id == models.User.id
        ).filter(
            (models.PrivateMessage.sender_id == user_id) | (models.PrivateMessage.recipient_id == user_id)
        )

        # Execute query
        messages = messages_query.all()

        # Filter and map results
        users_info = {}
        for message, user in messages:
            other_user_id = message.sender_id if message.recipient_id == user_id else message.recipient_id
            other_user = db.query(models.User).filter(models.User.id == other_user_id).first()

            # Determine if the message is read or not
            is_read = message.is_read if message.recipient_id == user_id else False

            # Update or add the user info
            if other_user_id not in users_info or not users_info[other_user_id].is_read:
                users_info[other_user_id] = schemas.PrivateInfoRecipient(
                    recipient_id=other_user_id,
                    recipient_name=other_user.user_name,
                    recipient_avatar=other_user.avatar,
                    verified=other_user.verified,
                    is_read=is_read
                )

        # Convert to list
        result = list(users_info.values())

        # Sort the list so that read messages (is_read = True) come first
        result.sort(key=lambda x: x.is_read, reverse=True)

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Sorry, no recipients or senders found.")
    except Exception as e:
        logger.error(f"Error creating {e}", exc_info=True)
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
    
# 