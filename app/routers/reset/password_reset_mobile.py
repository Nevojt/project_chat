from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import pytz
from datetime import datetime, timedelta

from app.models import user_model, password_model
from app.schemas.reset import PasswordResetRequest, PasswordResetMobile, PasswordResetV2

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
    
    mail_query = select(user_model.User).where(user_model.User.email == email.email, user_model.User.verified == True)
    result = await db.execute(mail_query)
    mail = result.one_or_none()
    
    if not mail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email {email.email} not found or user not verified")

    
    reset_code = utils.generate_reset_code()
    db_obj = password_model.PasswordReset(email=email.email, reset_code=reset_code)
    db.add(db_obj)
    await db.commit()
    await password_reset_mobile("Password Reset", email.email,
            {
                "title": "Password Reset",
                "reset_code": reset_code
            }
        )
    return {"msg": "Password reset email sent successfully."}


@router.post("/code_verification")
async def reset_password_v2_code(reset: PasswordResetV2, db: AsyncSession = Depends(get_async_session)):
    
    stmt = select(password_model.PasswordReset).where(password_model.PasswordReset.email == reset.email,
                                                 password_model.PasswordReset.reset_code == reset.code,
                                                 password_model.PasswordReset.is_active == True)
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
    
    return Response(status_code=status.HTTP_200_OK)

@router.post("/reset-password")
async def reset_password(reset: PasswordResetMobile, db: AsyncSession = Depends(get_async_session)):
    
    stmt = select(password_model.PasswordReset).where(password_model.PasswordReset.email == reset.email,
                                                 password_model.PasswordReset.reset_code == reset.code,
                                                 password_model.PasswordReset.is_active == True)
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
    
    stmt_update = update(user_model.User).where(user_model.User.email == reset.email).values(password=utils.hash(reset.password),
                                                                                     blocked=False,
                                                                                     password_changed=current_time_utc)
    result = await db.execute(stmt_update)
    await db.commit()
    
    stmt_delete = delete(password_model.PasswordReset).where(password_model.PasswordReset.email == reset.email)
    result = await db.execute(stmt_delete)
    await db.commit()
    return Response(status_code=status.HTTP_200_OK)
    
    