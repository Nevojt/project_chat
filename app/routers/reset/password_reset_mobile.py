from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import pytz
from datetime import datetime, timedelta

from app.models import models
from app.schemas.reset import PasswordResetRequest, PasswordResetMobile

from app.config import utils
from app.mail.send_mail import password_reset_mobile
from app.database.async_db import get_async_session


router = APIRouter(
    prefix="/password-reset-mobile",
    tags=["Password reset mobile"]
)



@router.post("/request-password-reset")
async def request_password_reset(email: PasswordResetRequest,
                                 db: AsyncSession = Depends(get_async_session)):
    
    mail_query = select(models.User).where(models.User.email == email.email, models.User.verified == True)
    result = await db.execute(mail_query)
    mail = result.one_or_none()
    
    if not mail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email {email.email} not found or user not verified")

    
    reset_code = utils.generate_reset_code()
    db_obj = models.PasswordReset(email=email.email, reset_code=reset_code)
    db.add(db_obj)
    await db.commit()
    await password_reset_mobile("Password Reset", email.email,
            {
                "title": "Password Reset",
                "reset_code": reset_code
            }
        )
    return {"msg": "Password reset email sent successfully."}

@router.post("/reset-password")
async def reset_password(reset: PasswordResetMobile, db: AsyncSession = Depends(get_async_session)):
    
    stmt = select(models.PasswordReset).where(models.PasswordReset.email == reset.email,
                                                 models.PasswordReset.reset_code == reset.code,
                                                 models.PasswordReset.is_active == True)
    result = await db.execute(stmt)
    reset_entry = result.scalars().first()
    
    timezone = pytz.timezone('UTC')
    current_time_utc = datetime.now(timezone)
    if not reset_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email {reset.email} not found or code reset not active")
        
    if current_time_utc > reset_entry.created_at + timedelta(hours=1):
        reset_entry.is_active = False
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Code reset not active")
    
    stmt_update = update(models.User).where(models.User.email == reset.email).values(password=utils.hash(reset.password), blocked=False, password_changed=current_time_utc)
    result = await db.execute(stmt_update)
    await db.commit()
    
    stmt_delete = delete(models.PasswordReset).where(models.PasswordReset.email == reset.email)
    result = await db.execute(stmt_delete)
    await db.commit()
    return {"msg": "Password reset successfully."}
    