from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.endpoints import auth, tasks, analytics, audit, reports, dashboard
from app.api import predictions, sentiment, blockchain
from app.api import notifications
from app.api import analytics_fraud
from app.api import assistant
from app.api import access_analytics  # NEW
from app.api import automation  # NEW
from app.api import data_transfer  # NEW
from app.api import dashboard_charts  # NEW
from app.middleware.access_logger import AccessLoggerMiddleware
from app.db.session import get_db

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

# Add access logging middleware
db = next(get_db())
app.add_middleware(AccessLoggerMiddleware, db_session=db)

# Include existing routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(predictions.router)
app.include_router(sentiment.router)
app.include_router(blockchain.router)
app.include_router(notifications.router)
app.include_router(analytics_fraud.router, prefix="/api/analytics")
app.include_router(assistant.router, prefix="/api/assistant")

# Include NEW routers
app.include_router(access_analytics.router)
app.include_router(automation.router)
app.include_router(data_transfer.router)
app.include_router(dashboard_charts.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Government Productivity Tracker API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME
    }
