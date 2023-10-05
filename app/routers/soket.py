
from fastapi import status, HTTPException, Depends, APIRouter, Response, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import asc, func
from app.database import get_db
from app import models, schemas, oauth2
from typing import List


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    
    messages = await get_images(db)
    serialized_messages = [row_to_dict(message) for message in messages]
    await websocket.send_json(serialized_messages)

    
    while True:
        data = await websocket.receive_text()
        
        try:
            message_data = schemas.Images.parse_raw(data)
            print(type(message_data))
            
        except WebSocketDisconnect:
            await websocket.close()
            
        except Exception as e:
            await websocket.send_text(f"Error parsing data: {str(e)}")
            continue 

        message = await create_image(message_data, db)
        await websocket.send_json(f"Message saved with ID: {message.images}")


async def get_images(db: Session = Depends(get_db)):
    posts = db.query(models.ImagesAll).all()
    return posts

async def create_image(images_data: schemas.ImagesCreate, db: Session = Depends(get_db)):
 
    image_instance = models.ImagesAll(**images_data.dict())
    db.add(image_instance)
    db.commit()
    db.refresh(image_instance)    
    return image_instance


def row_to_dict(row) -> dict:
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}
