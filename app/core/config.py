# from pydantic_settings import BaseSettings
# from typing import Optional

# class Settings(BaseSettings):
#     """Application settings loaded from environment variables"""
    
#     # App Info
#     APP_NAME: str = "Government Productivity Tracker"
#     DEBUG: bool = True
#     VERSION: str = "1.0.0"
    
#     # Database
#     DATABASE_URL: str
    
#     # Security
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    
#     # CORS (for frontend connection)
#     ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = True

# # Create global settings instance
# settings = Settings()
from pydantic_settings import BaseSettings # type: ignore
from typing import Optional, List

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Info
    APP_NAME: str = "Government Productivity Tracker"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./test.db"  # Default fallback value
    
    # Security
    SECRET_KEY: str = "your-default-secret-key-change-in-production"  # Default fallback value
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    
    # CORS (for frontend connection)
    ALLOWED_ORIGINS: List[str] = ("http://localhost:3000", "http://localhost:8080")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()
