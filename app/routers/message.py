from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(
    prefix="/messagesDev",
    tags=['MessageDev'],
)


@router.get("/")
async def get_posts(db: Session = Depends(get_db)): # , current_user: int = Depends(oauth2.get_current_user)
    posts = db.query(models.Message).all()
    return posts


@router.get("/{rooms}")
async def get_post(rooms: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):  # , current_user: int = Depends(oauth2.get_current_user)
    
    post = db.query(models.Message).filter(models.Message.rooms == rooms).all()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with rooms: {rooms} not found")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.MessagePost)
async def create_post(post: schemas.MessageCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): # , current_user: int = Depends(oauth2.get_current_user)
    
    # print(current_user.id)
    # print(current_user.user_name)
    post = models.Message(owner_id=current_user.id, **post.dict())
    db.add(post)
    db.commit()
    db.refresh(post)    
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Message).filter(models.Message.id == id)
    
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
        
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.MessagePost)
def update_post(id: int, update_post: schemas.MessageCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Message).filter(models.Message.id == id)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
        
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
    
    post_query.update(update_post.dict(), synchronize_session=False)
    
    db.commit()
    return post_query.first()