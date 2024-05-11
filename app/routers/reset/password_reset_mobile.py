from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import models
from app.schemas.reset import PasswordReset, PasswordResetRequest, PasswordResetMobile
from app.auth import oauth2
from app.config import utils
from app.mail.send_mail import password_reset_mobile
from app.database.database import get_db
from app.database.async_db import get_async_session


router = APIRouter(
    prefix="/password-reset-mobile",
    tags=["Password reset mobile"]
)



@router.post("/request-password-reset")
async def request_password_reset(email: PasswordResetRequest,
                                 db: AsyncSession = Depends(get_async_session)):
    
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