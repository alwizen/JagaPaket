import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from config import settings
from database import engine, Base, AsyncSessionLocal
from routers import auth, videos, users, devices
from models import User
from security import get_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create missing directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs(settings.VIDEO_STORAGE_PATH, exist_ok=True)

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
        
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
                logger.info("Default admin user created")
    except SQLAlchemyError as e:
        logger.error(f"Database initialization error - {str(e)}", exc_info=True)
        logger.error(f"DATABASE_URL: {settings.DATABASE_URL}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}", exc_info=True)
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # App Startup
    try:
        await init_db()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    yield
    # App Shutdown
    await engine.dispose()
    logger.info("Application shutdown complete")

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

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Check application and database health"""
    try:
        # Test database connection
        async with AsyncSessionLocal() as session:
            await session.execute(select(User).limit(1))
        return {
            "status": "healthy",
            "database": "connected",
            "project": settings.PROJECT_NAME
        }
    except SQLAlchemyError as e:
        logger.error(f"Health check - Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Health check - Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )

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
