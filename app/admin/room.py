from app.routers import user

from typing import List
from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# from ...auth import oauth2
# from ...database.async_db import get_async_session

from app.models import user_model
from app.schemas import user


router = APIRouter(
    prefix="/admin/rooms",
    tags=["Admin Rooms"],
)