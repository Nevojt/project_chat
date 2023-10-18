
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .database import engine
from .routers import message, socket, user, rooms, auth, user_status, vote, images
from app import models

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
app.include_router(socket.router)

app.include_router(user.router)


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})