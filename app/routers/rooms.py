from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/rooms",
    tags=['Rooms'],
)


@router.get("/")
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Rooms).all()
    return posts



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.RoomPost)
async def get_posts(post: schemas.RoomCreate, db: Session = Depends(get_db)):
    
    
    post = models.Rooms(**post.dict())
    db.add(post)
    db.commit()
    db.refresh(post)    
    return post



@router.get("/{name_room}", response_model=schemas.RoomPost)
async def get_post(name_room: str, db: Session = Depends(get_db)):
    post = db.query(models.Rooms).filter(models.Rooms.name_room == name_room).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with name_room: {name_room} not found")
    return post


@router.delete("/{name_room}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(name_room: str, db: Session = Depends(get_db)):
    post = db.query(models.Rooms).filter(models.Rooms.name_room == name_room)
    
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with name_room: {name_room} not found")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{name_room}", response_model=schemas.RoomPost)
def update_room(name_room: str, update_post: schemas.RoomCreate, db: Session = Depends(get_db)):
    
    post_query = db.query(models.Rooms).filter(models.Rooms.name_room == name_room)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with name_room: {name_room} not found")
    
    post_query.update(update_post.dict(), synchronize_session=False)
    
    db.commit()
    return post_query.first()