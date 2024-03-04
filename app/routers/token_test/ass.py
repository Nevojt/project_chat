
from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db

from app.auth import oauth2


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
        user = oauth2.verify_access_token(token, credentials_exception)
        return Response(status_code=status.HTTP_200_OK)
    except HTTPException as ex_error:
        raise ex_error