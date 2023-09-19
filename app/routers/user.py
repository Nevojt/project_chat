from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, utils, oauth2

router = APIRouter(
    prefix="/users",
    tags=['Users'],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def created_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(models.User).filter(models.User.user_name == user.user_name).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"User {existing_user.user_name} already exists")
    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user) 
    
    return new_user
     
        
    


@router.get('/{id}', response_model=schemas.UserOut)
def get_users(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} not found")
        
    return user