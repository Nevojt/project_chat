from fastapi import WebSocket, Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, oauth2
  # Import your token verification function

router = APIRouter()



@router.websocket("/ws")

async def websocket_endpoint(websocket: WebSocket, token: str = None, db: Session = Depends(get_db)):
    if token is None:
        await websocket.close(code=1008)  # Close the WebSocket connection if token is missing

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"}
        )
    
    token =  oauth2.verify_access_token(token, credentials_exception)  # Replace with your token verification function
    user = db.query(models.User).filter(models.User.id == token.id).first()

    if user is None:
        await websocket.close(code=1008)  # Close the WebSocket connection if the token is invalid

    await websocket.accept()
    await websocket.send_text(f"Welcome, {user.user_name}!")

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Received: {data}")