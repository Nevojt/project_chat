from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from app import models, oauth2, utils
from ..database import get_db, get_async_session


router = APIRouter(
    tags=["Verify"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/verify_email")
async def verify_email(token: str, request: Request, db: AsyncSession = Depends(get_async_session)):
    """
    Verifies the user's email address using the provided token.

    Args:
        token (str): The token received from the user's email.
        db (AsyncSession): Asynchronous database session.

    Raises:
        HTTPException: If the token is invalid or the user is not found.

    Returns:
        dict: A message confirming email verification.
    """
    user = await oauth2.get_current_user(token, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired token")

    user.verified = True
    db.add(user)
    await db.commit()

    return templates.TemplateResponse("success_registration.html", {"request": request})



