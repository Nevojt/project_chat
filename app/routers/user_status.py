from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(
    prefix="/user_status",
    tags=['User Status'],
)


@router.get("/")
async def get_posts(db: Session = Depends(get_db)): # , current_user: int = Depends(oauth2.get_current_user)
    posts = db.query(models.User_Status).all()
    return posts


@router.get("/{user_name}")
async def get_post(user_name: str, db: Session = Depends(get_db)):  # , current_user: int = Depends(oauth2.get_current_user)
    
    post = db.query(models.User_Status).filter(models.User_Status.user_name == user_name).all()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with user_name: {user_name} not found")
    return post

# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserStatusPost)
# async def create_posts(post: schemas.UserStatusCreate, db: Session = Depends(get_db)): # , current_user: int = Depends(oauth2.get_current_user)

    
#     # print(current_user.user_name)
#     post = models.User_Status(**post.dict())
#     db.add(post)
#     db.commit()
#     db.refresh(post)    
#     return post



@router.put("/{user_id}", response_model=schemas.UserStatusPost)
def update_post(user_id: int, update_post: schemas.UserStatusUpdate, db: Session = Depends(get_db)): # , current_user: int = Depends(oauth2.get_current_user)
    
    post_query = db.query(models.User_Status).filter(models.User_Status.user_id == user_id)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with user_id: {user_id} not found")
    
    post_query.update(update_post.dict(), synchronize_session=False)
    
    db.commit()
    return post_query.first()