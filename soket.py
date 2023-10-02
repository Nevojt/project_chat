
from fastapi import status, HTTPException, Depends, APIRouter, Response, WebSocket
from sqlalchemy.orm import Session
from app.database import get_db
router = APIRouter()

messages = ["hello", "world"]


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    # Відправте всі збережені повідомлення новому користувачеві
    for message in db:
        await websocket.send_text(message)

    # Очікуйте нові повідомлення
    while True:
        data = await websocket.receive_text()
        messages.append(data)  # Збережіть нове повідомлення
        await websocket.send_text(f"Повідомлення отримано: {data}")

active_websockets = []

@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()
    active_websockets.append((room, websocket))
    
    try:
        while True:
            data = await websocket.receive_text()
            # Відправте повідомлення всім підключеним користувачам в цій кімнаті
            for r, ws in active_websockets:
                if r == room:
                    await ws.send_text(data)
    except:
        # Коли користувач відключається, видаліть його веб-сокет зі списку
        active_websockets.remove((room, websocket))