import logging
from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db

from .. import oauth2

logging.basicConfig(filename='log/ass.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter(tags=['ASS'])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

@router.get('/ass')
def ass_endpoint(token: str, session: Session = Depends(get_db)):
    try:
        user = oauth2.verify_access_token(token, credentials_exception)
        return Response(status_code=status.HTTP_200_OK)
    except HTTPException as ex_error:
        raise ex_error