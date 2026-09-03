from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Drishti API"
    DATABASE_URL: str = "sqlite:///./drishti.db"
    SECRET_KEY: str = "drishti_super_secret_hackathon_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # For MVP, parse comma-separated strings or list directly
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
