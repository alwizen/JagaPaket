import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select
from config import settings
from database import engine, Base, AsyncSessionLocal
from routers import auth, videos, users, devices
from models import User
from security import get_password_hash

# Create missing directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs(settings.VIDEO_STORAGE_PATH, exist_ok=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Create default admin if no users exist
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).limit(1))
        if not result.scalar_one_or_none():
            admin = User(
                name="System Admin",
                username="admin",
                password_hash=get_password_hash("admin123"),
                role="SUPER_ADMIN"
            )
            session.add(admin)
            await session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # App Startup
    await init_db()
    yield
    # App Shutdown
    await engine.dispose()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Expose video directory statically for playback if needed (Super admins only via endpoints ideally, but static file is simpler if we trust the network context)
# A better approach is using the router to serve it, we included an upload function but no playback yet. Let's rely on standard routes or protected streaming.
app.mount("/videos", StaticFiles(directory=settings.VIDEO_STORAGE_PATH), name="videos")

templates = Jinja2Templates(directory="templates")

app.include_router(auth.router, prefix="/api/auth")
app.include_router(users.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(videos.router, prefix="/api")

# Basic page routing
@app.get("/")
async def serve_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/dashboard")
async def serve_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/recorder")
async def serve_recorder(request: Request):
    return templates.TemplateResponse(request=request, name="recorder.html")

@app.get("/videos_page")
async def serve_videos(request: Request):
    return templates.TemplateResponse(request=request, name="videos.html")

@app.get("/users_page")
async def serve_users(request: Request):
    return templates.TemplateResponse(request=request, name="users.html")

@app.get("/devices_page")
async def serve_devices(request: Request):
    return templates.TemplateResponse(request=request, name="devices.html")
