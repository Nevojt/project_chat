from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, utils, oauth2
from typing import List

router = APIRouter(
    prefix="/users",
    tags=['Users'],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def created_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"User {existing_user.email} already exists")
    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user) 
    
    post = models.User_Status(user_id=new_user.id, user_name=new_user.user_name, room_name="Holl")
    db.add(post)
    db.commit()
    db.refresh(post) 
    
    return new_user
     
        
    


@router.get('/{email}', response_model=schemas.UserInfo)
def get_user_mail(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email {email} not found")
        
    return user


@router.get("/", response_model=List[schemas.UserInfo])
async def get_email(db: Session = Depends(get_db)):
    posts = db.query(models.User).all()
    return posts