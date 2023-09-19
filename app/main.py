
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import message, user, rooms, auth, user_status
# from .config import settings



models.Base.metadata.create_all(bind=engine)

app = FastAPI()



app.include_router(message.router)
app.include_router(rooms.router)
app.include_router(auth.router)
app.include_router(user_status.router)

app.include_router(user.router)