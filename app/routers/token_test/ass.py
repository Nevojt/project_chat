
from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db

from app.auth import oauth2
from app.models.user_model import User


router = APIRouter(tags=['ASS'])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

@router.get('/ass')
def ass_endpoint(token: str, session: Session = Depends(get_db)):
    """_summary_

    Args:
        token (str): token verification
        session (Session, optional): session database. Defaults to Depends(get_db).

    Raises:
        HTTPException:: Token not validation

    Returns:
        Response: return server
    """
    
    try:
        user_data = oauth2.verify_access_token(token, credentials_exception)
        user = session.query(User).filter(User.id == user_data.id).first()
        
        if user.blocked == True:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {user.id} is blocked")

            
        return Response(status_code=status.HTTP_200_OK)
    except HTTPException as ex_error:
        raise ex_error