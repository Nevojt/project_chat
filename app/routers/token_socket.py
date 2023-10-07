from fastapi import WebSocket, Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, oauth2
from datetime import datetime
import json
  # Import your token verification function

router = APIRouter()



@router.websocket("/ws/{rooms}")

async def websocket_endpoint(websocket: WebSocket, rooms: str, token: str = None, db: Session = Depends(get_db)):
    if token is None:
        await websocket.close(code=1008)  # Close the WebSocket connection if token is missing

    user = oauth2.get_current_user(token, db)

    if user is None:
        await websocket.close(code=1008)  # Close the WebSocket connection if the token is invalid

    await websocket.accept()
    await websocket.send_text(f"Welcome, {user.user_name}!")
    
    messages = await get_messages(db, rooms)
    serialized_messages = [row_to_dict(message) for message in messages]
    await websocket.send_text(json.dumps(serialized_messages, ensure_ascii=False))

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Received: {data}")
        
        
        
        
async def get_messages(db: Session = Depends(get_db), rooms: str = None, current_user: int = Depends(oauth2.get_current_user)):
    query = db.query(models.Message)
    
    if rooms is not None:
        query = query.filter(models.Message.rooms == rooms)
    
    posts = query.all()
    return posts


def row_to_dict(row) -> dict:
    data =  {column.name: getattr(row, column.name) for column in row.__table__.columns}
    
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data

