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


@router.get("/")
async def get_all_private_messages(db: Session = Depends(get_db)):
    query = db.query(models.PrivateMessage).all()
    return query


@router.get("/{user_id}", response_model=List[schemas.PrivateInfoRecipient])
async def get_private_recipient(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a list of unique recipients and senders associated with a given user's private messages,
    prioritizing those where the messages have been read.

    Args:
        user_id (int): The ID of the user whose message recipients and senders are to be retrieved.
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Raises:
        HTTPException: Raises a 404 error if no recipients or senders are found for the given user.

    Returns:
        List[schemas.PrivateInfoRecipient]: A list of unique private message recipients and senders with their details.
    """
    
    # Query for recipients and senders without filtering by is_read
    messages_query = db.query(models.PrivateMessage, models.User).join(
        models.User, models.PrivateMessage.recipient_id == models.User.id
    ).filter(
        (models.PrivateMessage.sender_id == user_id) | (models.PrivateMessage.recipient_id == user_id)
    )

    # Execute query
    messages = messages_query.all()

    # Sort messages by is_read, prioritizing True
    messages.sort(key=lambda x: x[0].is_read, reverse=True)

    # Combine and filter results
    unique_users = {}
    for message, user in messages:
        # Визначаємо, хто є одержувачем у повідомленні
        if message.sender_id == user_id:
            # Якщо користувач є відправником, то одержувачем є інша сторона
            other_user_id = message.recipient_id
        else:
            # Якщо користувач є одержувачем, то відправником є інша сторона
            other_user_id = message.sender_id

        # Отримуємо деталі іншого користувача
        other_user = db.query(models.User).filter(models.User.id == other_user_id).first()

        if other_user_id not in unique_users or (other_user_id in unique_users and message.is_read):
            unique_users[other_user_id] = schemas.PrivateInfoRecipient(
                recipient_id=other_user_id,
                recipient_name=other_user.user_name,
                recipient_avatar=other_user.avatar,
                verified=other_user.verified,
                is_read=message.is_read
            )

    result = list(unique_users.values())

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