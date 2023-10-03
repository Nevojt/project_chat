
from fastapi import status, HTTPException, Depends, APIRouter, Response, WebSocket
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/ws",
    tags="Socket"
)



@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        message_data = schemas.MessagePost.parse_raw(data)
        message = save_message(db, message_data)
        await websocket.send_text(f"Message saved with ID: {message.id}")



def save_message(db: Session, message_data: schemas.MessagePost):
    message = models.Message(**message_data.dict())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message