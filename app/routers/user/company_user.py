
from typing import List
from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import oauth2
from ...database.async_db import get_async_session

from app.models import user_model
from app.schemas import user



router = APIRouter(
    prefix="/company-users",
    tags=["Company Users"],
)


@router.get("/{company_id}", response_model=List[user.UserInfoLights])
async def read_company_users(company_id: int,
                             db: AsyncSession = Depends(get_async_session),
                             current_user: user.UserOut = Depends(oauth2.get_current_user)):
    
    query_users = select(user_model.User).where(user_model.User.company_id == company_id)
    result = await db.execute(query_users)
    users = result.scalars().all()
    
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Company with ID: {company_id} not found")
    
    return users