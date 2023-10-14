from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(
    prefix="/images",
    tags=['Images'],
)


@router.get("/")
async def get_images(db: Session = Depends(get_db)):
    posts = db.query(models.ImagesAll).all()
    return posts



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ImagesResponse)
async def create_image(images: schemas.ImagesCreate, db: Session = Depends(get_db)):
 
    images = models.ImagesAll(**images.model_dump())
    db.add(images)
    db.commit()
    db.refresh(images)    
    return images



@router.get("/{image_room}")
async def get_room(image_room: str, db: Session = Depends(get_db)):
    post = db.query(models.ImagesAll).filter(models.ImagesAll.image_room == image_room).all()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with image_room: {image_room} not found")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(id: int, db: Session = Depends(get_db)):
    post = db.query(models.ImagesAll).filter(models.ImagesAll.id == id)
    
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image_room with: {id} not found")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)