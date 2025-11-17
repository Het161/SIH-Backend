import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "SmartWork 360"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None
    
    # Frontend URL
    FRONTEND_URL: str = "https://smartwork-frontend-2242.vercel.app"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://smartwork-frontend-2242.vercel.app",
        "https://sih-backend-xiz8.onrender.com",
    ]
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465  # ✅ Changed from 462 to 465
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str
    SMTP_FROM_NAME: str = "SmartWork 360"
    
    # Optional Services
    REDIS_URL: Optional[str] = None
    CELERY_BROKER_URL: Optional[str] = None
    
    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set default DATABASE_URL if not provided
        if not self.DATABASE_URL:
            self.DATABASE_URL = "postgresql://user:password@localhost/dbname"


settings = Settings()



