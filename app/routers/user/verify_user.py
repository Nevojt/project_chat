from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.templating import Jinja2Templates
from app.models import user_model
from app.database.async_db import get_async_session


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/success_registration", include_in_schema=False)
async def verify_email(token: str, request: Request, db: AsyncSession = Depends(get_async_session)):
    """
    Verifies the user's email address using the provided token.
    
    Verifies the user's email address using the provided token.

    Args:
        token (str): The token received from the user's email.
        db (AsyncSession): Asynchronous database session.

    Raises:
        HTTPException: If the token is invalid or the user is not found.

    Returns:
        dict: A message confirming email verification.
    """
    # Query for a user with the matching token_verify field
    # Construct the query
    query = select(user_model.User).where(user_model.User.token_verify == token)

    # Execute the query
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return templates.TemplateResponse("error_page.html", {"request": request})
        

    # Update the user's verified status
    user.verified = True
    user.token_verify = None  # Clear the token once verified
    await db.commit()

    return templates.TemplateResponse("success_registration.html", {"request": request})