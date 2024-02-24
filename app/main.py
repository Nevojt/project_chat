
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .database import engine
from .routers import message, upload_file_supabase, user, rooms, auth, user_status, vote, images, private_messages, count_users_messages, password_reset, verify_user
from .routers import upload_file_google, ass
from app import models, send_mail

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    root_path="/api"
    title="Cool Chat",
    description="Cool Chat",
    docs_url="/docs",
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
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(user_status.router)
app.include_router(vote.router)
app.include_router(images.router)

app.include_router(private_messages.router)
app.include_router(count_users_messages.router)
app.include_router(password_reset.router)
app.include_router(send_mail.router)

app.include_router(verify_user.router)
app.include_router(upload_file_supabase.router)
app.include_router(upload_file_google.router)
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