import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Warehouse Packing Proof Recording System"
    # Using sqlite for testing since MariaDB setup is missing on sandbox
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./recorderd.db")
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-replace-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    VIDEO_STORAGE_PATH: str = os.getenv("VIDEO_STORAGE_PATH", "./videos")

settings = Settings() 
