from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, oauth2, utils
from app.send_mail import password_reset
from ..database import get_db, get_async_session
from app.schemas import PasswordReset, PasswordResetRequest




router = APIRouter(
    prefix="/password",
    tags=["Password reset"]
)


@router.post("/request/", response_description="Reset password")
async def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Handles the password reset request. Validates the user's email and initiates the password reset process.

    Args:
        request (PasswordResetRequest): The request payload containing the user's email.
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Raises:
        HTTPException: Raises a 404 error if no user is found with the provided email.
        HTTPException: Raises a 404 error if the user's details are not found or the email address is invalid.

    Returns:
        dict: A message confirming that an email has been sent for password reset instructions.
    """
    # Func
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email: {request.email} not found")
    if user is not None:
        token = oauth2.create_access_token(data={"user_id": user.id})
        reset_link = f"http://127.0.0.1:8000/reset?token={token}"
        
        await password_reset("Password Reset", user.email,
            {
                "title": "Password Reset",
                "name": user.user_name,
                "reset_link": reset_link
            }
        )
        return {"msg": "Email has been sent with instructions to reset your password."}
        
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your details not found, invalid email address"
        )
        
        
@router.put("/reset/", response_description="Reset password")
async def reset(token: str, new_password: PasswordReset, db: AsyncSession = Depends(get_async_session)):
    """
    Handles the actual password reset using a provided token. Validates the token and updates the user's password.

    Args:
        token (str): The token for user verification, used to ensure the password reset request is valid.
        new_password (PasswordReset): The payload containing the new password.
        db (AsyncSession, optional): Asynchronous database session. Defaults to Depends(get_async_session).

    Raises:
        HTTPException: Raises a 404 error if no user is found associated with the provided token.

    Returns:
        dict: A message confirming that the password has been successfully reset.
    """
    
    user = await oauth2.get_current_user(token, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Хешування нового пароля
    hashed_password = utils.hash(new_password.password)

    # Оновлення пароля в базі даних
    user.password = hashed_password
    db.add(user)
    await db.commit()

    return {"msg": "Password has been reset successfully."}