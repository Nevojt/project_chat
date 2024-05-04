
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .mail import send_mail

from .routers.user import auth, finds, user, verify_user, user_status
from .routers.messages import message, private_messages, vote
from .routers.images import images, upload_file_google, upload_file_supabase, upload_and_return
from .routers.room import rooms, count_users_messages, secret_rooms, tabs_rooms, user_rooms, ban_user
from .routers.invitations import invitation_secret_room
from .routers.token_test import ass
from .routers.reset import password_reset
from .database.database import engine
from app.models import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    root_path="/api",
    docs_url="/docs",
    title="Chat",
    description="Chat documentation",
    version="0.1.3"
)

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
app.include_router(user_rooms.router)
app.include_router(secret_rooms.router)
app.include_router(invitation_secret_room.router)
app.include_router(tabs_rooms.router)
app.include_router(ban_user.router)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(finds.router)
app.include_router(user_status.router)
app.include_router(vote.router)

app.include_router(images.router)
app.include_router(upload_file_supabase.router)
app.include_router(upload_file_google.router)
app.include_router(upload_and_return.router)

app.include_router(private_messages.router)
app.include_router(count_users_messages.router)
app.include_router(password_reset.router)
app.include_router(send_mail.router)

app.include_router(verify_user.router)

app.include_router(ass.router)




app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", include_in_schema=False)
async def home(request: Request):
    return RedirectResponse(url="https://yura-platonov.github.io/Team-Chat/")


@app.get("/reset", include_in_schema=False)
async def read_reset(request: Request):
    return templates.TemplateResponse("window_new_password.html", {"request": request})

@app.get("/success-page", include_in_schema=False)
async def finally_reset(request: Request):
    return templates.TemplateResponse("success-page.html", {"request": request})

@app.get('/privacy-policy', include_in_schema=False)
async def privacy_policy(request: Request):
    return RedirectResponse(url="https://yura-platonov.github.io/Team-Chat/#/PrivacyPolicy")

# commit changes