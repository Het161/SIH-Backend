import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.core.config import settings
from app.db.session import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"📦 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🗄️  Database: {settings.DATABASE_URL[:40]}...")
    
    try:
        from app.models import User, Task  # Import models
        
        # Create tables only if they don't exist
        if settings.ENVIRONMENT != "production":
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created/verified")
        else:
            logger.info("✅ Database tables skipped (use Alembic in production)")
        
        # Test database connection
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)
    
    logger.info("✅ Application startup complete")
    yield
    logger.info("🛑 Application shutting down...")
    engine.dispose()
    logger.info("👋 Application shutdown complete")

app = FastAPI(
    title=settings.APP_NAME,
    description="SmartWork 360 - Government Productivity Management System",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS configuration - FIXED VERSION
def get_cors_origins():
    """Get CORS origins with safe attribute checking"""
    origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # Safely get FRONTEND_URL from environment or settings
    frontend_url = os.getenv("FRONTEND_URL")
    if not frontend_url and hasattr(settings, 'FRONTEND_URL'):
        frontend_url = settings.FRONTEND_URL
    if frontend_url:
        origins.append(frontend_url)
    
    # Safely get ALLOWED_ORIGINS from environment or settings
    allowed_origins = os.getenv("ALLOWED_ORIGINS")
    if not allowed_origins and hasattr(settings, 'ALLOWED_ORIGINS'):
        allowed_origins = settings.ALLOWED_ORIGINS
    
    if allowed_origins:
        if isinstance(allowed_origins, list):
            origins.extend(allowed_origins)
        elif isinstance(allowed_origins, str):
            # Split by comma if multiple origins
            origins.extend([origin.strip() for origin in allowed_origins.split(",")])
    
    # Allow all in development
    if settings.ENVIRONMENT == "development":
        logger.warning("⚠️  CORS: Allow all origins (development mode)")
        return ["*"]
    
    logger.info(f"🔒 CORS allowed origins: {origins}")
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail} | Path: {request.url.path} | Method: {request.method}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path)
            },
        },
        headers=getattr(exc, 'headers', None),
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors_list = []
    for error in exc.errors():
        error_dict = {
            "type": error.get("type"),
            "loc": list(error.get("loc", [])),
            "msg": error.get("msg"),
        }
        if "input" in error and not isinstance(error["input"], bytes):
            error_dict["input"] = str(error["input"])
        errors_list.append(error_dict)
    
    logger.warning(f"Validation Error: {request.url.path} | Errors: {errors_list}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "message": "Validation error - please check your request data",
                "status_code": 422,
                "details": errors_list,
            }
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled Exception: {type(exc).__name__} | Path: {request.url.path} | Error: {str(exc)}",
        exc_info=True
    )
    error_detail = str(exc) if settings.ENVIRONMENT == "development" else "Internal server error"
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "message": error_detail,
                "type": type(exc).__name__,
                "status_code": 500
            }
        },
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📨 {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"✅ {request.method} {request.url.path} | Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ {request.method} {request.url.path} | Error: {str(e)}", exc_info=True)
        raise

# Root endpoints
@app.get("/", tags=["Root"])
async def root():
    return {
        "success": True,
        "message": "Welcome to SmartWork 360 API",
        "data": {
            "app_name": settings.APP_NAME,
            "description": "Government Productivity Management System",
            "version": settings.VERSION,
            "status": "running",
            "environment": settings.ENVIRONMENT,
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "ready": "/ready",
                "info": "/info",
                "api": "/api/v1",
            },
        },
    }

@app.get("/health", tags=["Health"])
async def health_check():
    db_status = "unknown"
    db_error = None
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
        logger.error(f"Health check failed: {e}")
    
    is_healthy = db_status == "healthy"
    status_code = 200 if is_healthy else 503
    
    return JSONResponse(
        content={
            "success": is_healthy,
            "status": "healthy" if is_healthy else "unhealthy",
            "data": {
                "app_name": settings.APP_NAME,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "database": {
                    "status": db_status,
                    "error": db_error if not is_healthy else None
                },
            },
        },
        status_code=status_code,
    )

@app.get("/ready", tags=["Health"])
async def readiness_check():
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "success": True,
            "status": "ready",
            "message": "Application is ready to receive traffic",
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "status": "not_ready",
                "message": "Application is not ready",
                "error": str(e) if settings.ENVIRONMENT == "development" else None,
            },
        )

@app.get("/info", tags=["Info"])
async def api_info():
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": sorted(list(route.methods)),
                "name": route.name,
                "tags": getattr(route, "tags", [])
            })
    
    routes_by_tag = {}
    for route in routes:
        tags = route.get("tags", ["Untagged"])
        for tag in tags:
            if tag not in routes_by_tag:
                routes_by_tag[tag] = []
            routes_by_tag[tag].append({
                "path": route["path"],
                "methods": route["methods"]
            })
    
    return {
        "success": True,
        "data": {
            "app_name": settings.APP_NAME,
            "version": settings.VERSION,
            "total_routes": len(routes),
            "routes_by_tag": routes_by_tag
        }
    }

# Include API routers
from app.api.v1.endpoints import auth
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
logger.info("✅ Authentication routes loaded")

# Load additional v1 routes
try:
    from app.api.v1.endpoints import tasks, analytics, audit, reports, dashboard
    app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
    app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
    app.include_router(audit.router, prefix="/api/v1", tags=["Audit"])
    app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
    app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
    logger.info("✅ Additional v1 routes loaded")
except ImportError as e:
    logger.warning(f"⚠️  Some v1 routes not available: {e}")

# Load additional API routes (skip ML-dependent ones in production)
try:
    # Skip ML/AI routes in production to save memory
    if settings.ENVIRONMENT == "development":
        try:
            from app.api import predictions, sentiment, assistant
            app.include_router(predictions.router)
            app.include_router(sentiment.router)
            app.include_router(assistant.router)
            logger.info("✅ ML/AI routes loaded (development only)")
        except ImportError as ml_error:
            logger.warning(f"⚠️  ML/AI routes not available: {ml_error}")
    
    # Load non-ML routes
    from app.api import blockchain, notifications
    from app.api import analytics_fraud, access_analytics, automation
    from app.api import data_transfer, dashboard_charts
    
    app.include_router(blockchain.router)
    app.include_router(notifications.router)
    app.include_router(analytics_fraud.router)
    app.include_router(access_analytics.router)
    app.include_router(automation.router)
    app.include_router(data_transfer.router)
    app.include_router(dashboard_charts.router)
    logger.info("✅ Additional API routes loaded")
    
except ImportError as e:
    logger.warning(f"⚠️  Some API routes not available: {e}")

# Run server (for local development)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = settings.ENVIRONMENT == "development"
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    logger.info(f"🔄 Auto-reload: {reload}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )






