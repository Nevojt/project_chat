from datetime import datetime
from typing import List, Union
from fastapi import Form, Response, status, HTTPException, Depends, APIRouter, UploadFile, File, Query

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import utils
from app.config.config import settings
from .hello import say_hello_system, system_notification_change_owner
from .created_image import generate_image_with_letter
from ...auth import oauth2
from ...database.async_db import get_async_session
from ...database.database import get_db
from app.models import models
from app.schemas import user



router = APIRouter(
    prefix="/company-users",
    tags=["Company Users"],
)


@router.get("/{company_id}", response_model=List[user.UserInfo])
async def read_company_users(company_id: int,
                             db: AsyncSession = Depends(get_async_session),
                             current_user: user.UserOut = Depends(oauth2.get_current_user)):
    
    query_users = select(models.User).where(models.User.company_id == company_id)
    result = await db.execute(query_users)
    users = result.scalars().all()
    
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Company with ID: {company_id} not found")
    
    return users