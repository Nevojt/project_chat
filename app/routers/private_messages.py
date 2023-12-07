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


@router.get("/{user_id}", response_model=List[schemas.PrivateInfoRecipient])
async def get_private_recipient(user_id: int, db: Session = Depends(get_db)):
    
    """
    Retrieves a list of unique recipients and senders associated with a given user's private messages.

    Args:
        user_id (int): The ID of the user whose message recipients and senders are to be retrieved.
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Raises:
        HTTPException: Raises a 404 error if no recipients or senders are found for the given user.

    Returns:
        List[schemas.PrivateInfoRecipient]: A list of unique private message recipients and senders with their details.
    """
    
    # Query for recipients to whom the user sent messages
    sent_messages_query = db.query(models.PrivateMessage, models.User).distinct(models.PrivateMessage.recipient_id).join(
        models.User, models.PrivateMessage.recipient_id == models.User.id
    ).filter(
        models.PrivateMessage.sender_id == user_id
    )

    # Query for senders who sent messages to the user
    received_messages_query = db.query(models.PrivateMessage, models.User).distinct(models.PrivateMessage.sender_id).join(
        models.User, models.PrivateMessage.sender_id == models.User.id
    ).filter(
        models.PrivateMessage.recipient_id == user_id
    )

    # Execute queries
    sent_messages = sent_messages_query.all()
    received_messages = received_messages_query.all()

    # Combine results
    unique_users = {}
    for message, user in sent_messages + received_messages:
        user_id = user.id
        if user_id not in unique_users:
            unique_users[user_id] = schemas.PrivateInfoRecipient(
                recipient_id=user_id,
                recipient_name=user.user_name,
                recipient_avatar=user.avatar,
                is_read=message.is_read
            )

    result = list(unique_users.values())

    if not result:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Sorry, no recipients or senders found.")
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