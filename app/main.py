
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import message, user, rooms, auth, user_status, vote, images
from app import models, database, schemas, oauth2

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(message.router)
app.include_router(rooms.router)
app.include_router(auth.router)
app.include_router(user_status.router)
app.include_router(vote.router)
app.include_router(images.router)

app.include_router(user.router)



from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Message text was: {data}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(database.get_db)):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        
        # Try to parse the received data as JSON
        try:
            message_data = schemas.MessagePost.parse_raw(data)
        except Exception as e:
            await websocket.send_text(f"Error parsing data: {str(e)}")
            continue  # Go back to the beginning of the loop

        # If parsing was successful, save the message and send a confirmation
        message = save_message(db, message_data)
        await websocket.send_text(f"Message saved with ID: {message.id}")

def save_message(db: Session, message_data: schemas.MessageCreate):
    message = models.Message(**message_data.dict())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
