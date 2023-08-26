from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/room_one",
    tags=['Post'],
)


@router.get("/")
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def get_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    
    
    post = models.Post(**post.dict())
    db.add(post)
    db.commit()
    db.refresh(post)    
    return post



@router.get("/{id}", response_model=schemas.Post)
async def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, update_post: schemas.PostCreate, db: Session = Depends(get_db)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    
    post_query.update(update_post.dict(), synchronize_session=False)
    
    db.commit()
    return post_query.first()