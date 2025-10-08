from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import tasks
from app.api.v1.endpoints import analytics
from app.api.v1.endpoints import audit
from app.api.v1.endpoints import reports
from app.api.v1.endpoints import dashboard
# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Productivity Measurement Module for Government Offices",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tasks.router , prefix="/api/v1")
app.include_router(analytics.router , prefix="/api/v1")
app.include_router(audit.router , prefix="/api/v1")
app.include_router(reports.router , prefix="/api/v1")
app.include_router(dashboard.router , prefix="/api/v1")
# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Government Productivity Tracker API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME
    }
