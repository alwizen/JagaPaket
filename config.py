import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from pydantic import computed_field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Warehouse Packing Proof Recording System"
    
    # Database individual components
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "recorderd")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        # Priority 1: Direct DATABASE_URL from environment
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        # Priority 2: Construct from components
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-replace-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    VIDEO_STORAGE_PATH: str = os.getenv("VIDEO_STORAGE_PATH", "./videos")

settings = Settings()
