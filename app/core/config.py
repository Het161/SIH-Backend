import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "SmartWork 360"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"  # Default to production
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS (optional)
    FRONTEND_URL: Optional[str] = None
    ALLOWED_ORIGINS: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set JWT_SECRET_KEY to SECRET_KEY if not provided
        if not self.JWT_SECRET_KEY:
            self.JWT_SECRET_KEY = self.SECRET_KEY

settings = Settings()

