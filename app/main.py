
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .database import engine
from .routers import message, user, rooms, auth, user_status, vote, images, private_messages, count_users_messages, password_reset
from app import models, send_mail

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
app.include_router(private_messages.router)
app.include_router(count_users_messages.router)
app.include_router(password_reset.router)
app.include_router(send_mail.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
