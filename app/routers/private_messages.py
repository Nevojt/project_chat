from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(
    prefix="/private",
    tags=['Private'],
)


@router.get("/")
async def get_rooms(db: Session = Depends(get_db)):
    posts = db.query(models.PrivateMessage).all()
    return posts



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.RoomPost)
async def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    
    existing_room = db.query(models.Rooms).filter(models.Rooms.name_room == room.name_room).first()
    if existing_room:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"Room {existing_room.name_room} already exists")
    
    room = models.Rooms(**room.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)    
    return room