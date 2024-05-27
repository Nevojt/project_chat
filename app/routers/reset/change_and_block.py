from fastapi import Response, status, HTTPException, Depends, APIRouter, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mail import send_mail


from ...config import utils
from ...auth import oauth2
from ...database.async_db import get_async_session
from ...database.database import get_db
from app.models import models
from app.schemas import user
from typing import Annotated, List

router = APIRouter(
    prefix="/manipulation",
    tags=["Change password and blocked account"],
)


@router.put("/password", response_description="Reset password")
async def reset(password: user.UserUpdatePassword,
                db: AsyncSession = Depends(get_async_session),
                current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Reset the password of the currently authenticated user.

    Args:
        password (schemas.UserUpdatePassword): The new password and confirmation.
        db (AsyncSession): The database session to use.
        current_user (models.User): The currently authenticated user.

    Returns:
        dict: A message indicating that the password was reset successfully.

    Raises:
        HTTPException: If the user is not found, if the old password is incorrect, or if the new passwords do not match.
    """
    if current_user.verified == False or current_user.blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is not verified or blocked")
        
    query = select(models.User).where(models.User.id == current_user.id)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not utils.verify(password.old_password, existing_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )

    # hashed new password
    hashed_password = utils.hash(password.new_password)

    # Update password to database
    current_user.password = hashed_password
    db.add(current_user)
    await db.commit()
    
    token = current_user.refresh_token
    blocked_link = f"https://cool-chat.club/api/manipulation/blocked?token={token}"
    await send_mail.send_mail_for_change_password("Changing your account password", current_user.email,
            {
                "title": "Changing your account password",
                "name": current_user.user_name,
                "blocked_link": blocked_link
            }
        )

    return {"msg": "Password has been reset successfully."}

templates = Jinja2Templates(directory="templates")
@router.get("/blocked")
async def block_account(token: str, request: Request, db: AsyncSession = Depends(get_async_session)):
    
    user = await oauth2.get_current_user(token, db)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.blocked = True
    db.add(user)
    await db.commit()
    
    return templates.TemplateResponse("success-page.html", {"request": request})