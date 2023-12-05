from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app import models, oauth2
from ..database import get_db
from app.schemas import PasswordReset




router = APIRouter(
    prefix="/password",
    tags=["Password reset"]
)


@router.post("/", response_description="Reset password")
async def reset_password(request: PasswordReset, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email: {request.email} not found")
    if user is not None:
        token = oauth2.create_access_token(data={"user_id": user.id})
        reset_link = f"http://locahost:8000/reset?token={token}"
        
        
        
        
        return {
            "message": f"Password reset link sent to {request.email}",
            "token": token
        }