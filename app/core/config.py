# import os
# from pydantic_settings import BaseSettings
# from pydantic import ConfigDict
# from typing import List, Optional


# class Settings(BaseSettings):
#     # App Info
#     APP_NAME: str = "SmartWork 360"
#     VERSION: str = "1.0.0"
#     ENVIRONMENT: str = "productions"
    
#     # Server Configuration
#     HOST: str = "0.0.0.0"
#     PORT: int = 8000
    
#     # Database Configuration
#     DATABASE_URL: Optional[str] = None
    
#     # Frontend URL
#     FRONTEND_URL: str = "https://smartwork-frontend-2242.vercel.app"
    
#     # Security
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
#     # CORS Origins
#     CORS_ORIGINS: List[str] = [
#         "http://localhost:3000",
#         "http://localhost:3001",
#         "http://localhost:8000",
#         "http://127.0.0.1:3000",
#         "http://127.0.0.1:8000",
#         "https://smartwork-frontend-2242.vercel.app",
#         "https://sih-backend-xiz8.onrender.com",
#     ]
    
#     # Email Configuration
#     SMTP_HOST: str = "smtp.gmail.com"
#     SMTP_PORT: int = 465  # ✅ Changed from 462 to 465
#     SMTP_USER: str
#     SMTP_PASSWORD: str
#     SMTP_FROM: str
#     SMTP_FROM_NAME: str = "SmartWork 360"
    
#     # Optional Services
#     REDIS_URL: Optional[str] = None
#     CELERY_BROKER_URL: Optional[str] = None
    
#     model_config = ConfigDict(
#         env_file='.env',
#         env_file_encoding='utf-8',
#         case_sensitive=True,
#         extra='ignore'
#     )
    
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
        
#         # Set default DATABASE_URL if not provided
#         if not self.DATABASE_URL:
#             self.DATABASE_URL = "postgresql://user:password@localhost/dbname"


# settings = Settings()





import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, validator
from typing import List, Optional


class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "SmartWork 360"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"  # ✅ production/staging/development
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False  # ✅ NEVER True in production
    
    # Database Configuration
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    
    # Frontend URL
    FRONTEND_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Policy
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_SPECIAL_CHAR: bool = True
    REQUIRE_NUMBER: bool = True
    
    # CORS Origins
    CORS_ORIGINS: List[str] = []
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str
    SMTP_FROM_NAME: str = "SmartWork 360"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "app.log"
    
    # Monitoring (Optional)
    SENTRY_DSN: Optional[str] = None
    
    # Feature Flags
    ENABLE_SWAGGER_DOCS: bool = False  # ✅ Disable in production
    ENABLE_EMAIL_VERIFICATION: bool = True
    ENABLE_TWO_FACTOR_AUTH: bool = False
    
    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, v):
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'ENVIRONMENT must be one of {allowed}')
        return v
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters')
        return v
    
    @validator('CORS_ORIGINS', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v


settings = Settings()
