# """
# SmartWork 360 - FastAPI Backend Application
# Government Productivity Management System
# """
# import os
# from contextlib import asynccontextmanager
# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from fastapi.exceptions import RequestValidationError
# from starlette.exceptions import HTTPException as StarletteHTTPException
# import logging

# from app.core.config import settings
# from app.db.session import engine, Base

# # ============================================================================
# # LOGGING CONFIGURATION
# # ============================================================================
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
#     handlers=[logging.StreamHandler()],
# )
# logger = logging.getLogger(__name__)

# # ============================================================================
# # ENVIRONMENT CONFIGURATION
# # ============================================================================
# ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
# logger.info(f"🌍 Environment: {ENVIRONMENT}")


# # ============================================================================
# # APPLICATION LIFESPAN MANAGER
# # ============================================================================
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Startup and shutdown events handler"""
#     app_name = getattr(settings, 'APP_NAME', 'SmartWork 360')
#     version = getattr(settings, 'VERSION', '1.0.0')
    
#     # Startup
#     logger.info("=" * 60)
#     logger.info(f"🚀 Starting {app_name} v{version}")
#     logger.info(f"📦 Environment: {ENVIRONMENT}")
#     logger.info(f"🗄️  Database: {settings.DATABASE_URL[:40]}...")
#     logger.info("=" * 60)
    
#     try:
#         # Import models to ensure they're registered
#         from app.models import User, Task
        
#         # Create tables in development (use Alembic in production)
#         if ENVIRONMENT != "production":
#             Base.metadata.create_all(bind=engine)
#             logger.info("✅ Database tables created/verified")
#         else:
#             logger.info("✅ Database tables management: Use Alembic migrations")
        
#         # Test database connection
#         from sqlalchemy import text
#         with engine.connect() as conn:
#             conn.execute(text("SELECT 1"))
#         logger.info("✅ Database connection successful")
        
#     except Exception as e:
#         logger.error(f"❌ Database initialization error: {e}", exc_info=True)
#         logger.warning("⚠️  Application will continue but database operations may fail")
    
#     logger.info("=" * 60)
#     logger.info("✅ Application startup complete")
#     logger.info("=" * 60)
    
#     yield
    
#     # Shutdown
#     logger.info("=" * 60)
#     logger.info("🛑 Application shutting down...")
#     engine.dispose()
#     logger.info("✅ Database connections closed")
#     logger.info("👋 Application shutdown complete")
#     logger.info("=" * 60)


# # ============================================================================
# # FASTAPI APPLICATION INITIALIZATION
# # ============================================================================
# app = FastAPI(
#     title=getattr(settings, 'APP_NAME', 'SmartWork 360'),
#     description="Government Productivity Management System - Backend API",
#     version=getattr(settings, 'VERSION', '1.0.0'),
#     docs_url="/docs",
#     redoc_url="/redoc",
#     openapi_url="/openapi.json",
#     lifespan=lifespan,
# )


# # ============================================================================
# # CORS CONFIGURATION
# # ============================================================================
# def get_allowed_origins():
#     """Get list of allowed CORS origins based on environment"""
#     origins = [
#         # Production URLs
#         "https://smartwork-frontend-2242.vercel.app",  # Your Vercel frontend
#         "https://sih-backend-xiz8.onrender.com",       # Backend itself
        
#         # Development URLs
       
       
#         "http://localhost:3000",
#         "http://localhost:3001",
#         "http://localhost:8000",
#         "http://127.0.0.1:3000",
#         "http://127.0.0.1:8000",
#         "https://smartwork-frontend-2242.vercel.app",
#         settings.FRONTEND_URL 
#     ]
    
#     # Add FRONTEND_URL from environment
#     frontend_url = os.getenv("FRONTEND_URL")
#     if frontend_url:
#         origins.append(frontend_url)
#         logger.info(f"✅ Added FRONTEND_URL from env: {frontend_url}")
    
#     # Add comma-separated ALLOWED_ORIGINS from environment
#     allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
#     if allowed_origins_env:
#         extra_origins = [o.strip() for o in allowed_origins_env.split(",")]
#         origins.extend(extra_origins)
#         logger.info(f"✅ Added ALLOWED_ORIGINS from env: {extra_origins}")
    
#     # Development mode: allow all origins
#     if ENVIRONMENT == "development":
#         origins.append("*")
#         logger.warning("⚠️  CORS: Allowing ALL origins (development mode)")
    
#     # Log all allowed origins
#     logger.info(f"🔒 CORS allowed origins ({len(origins)} total):")
#     for origin in origins:
#         logger.info(f"   - {origin}")
    
#     return origins


# # Apply CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS + [settings.FRONTEND_URL],
#     allow_origins=get_allowed_origins(),
#     allow_credentials=True, 
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["*"],
# )
# logger.info("✅ CORS middleware configured")


# # ============================================================================
# # EXCEPTION HANDLERS
# # ============================================================================
# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler(request: Request, exc: StarletteHTTPException):
#     """Handle HTTP exceptions"""
#     logger.warning(
#         f"HTTP {exc.status_code}: {exc.detail} | "
#         f"Path: {request.url.path} | Method: {request.method}"
#     )
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "success": False,
#             "error": {
#                 "message": exc.detail,
#                 "status_code": exc.status_code,
#                 "path": str(request.url.path),
#                 "method": request.method,
#             },
#         },
#         headers=getattr(exc, 'headers', None),
#     )


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     """Handle request validation errors"""
#     errors_list = []
#     for error in exc.errors():
#         error_dict = {
#             "type": error.get("type"),
#             "loc": list(error.get("loc", [])),
#             "msg": error.get("msg"),
#         }
#         if "input" in error and not isinstance(error["input"], bytes):
#             error_dict["input"] = str(error["input"])
#         errors_list.append(error_dict)
    
#     logger.warning(
#         f"Validation Error: {request.url.path} | "
#         f"Method: {request.method} | Errors: {len(errors_list)}"
#     )
    
#     return JSONResponse(
#         status_code=422,
#         content={
#             "success": False,
#             "error": {
#                 "message": "Validation error - please check your request data",
#                 "status_code": 422,
#                 "path": str(request.url.path),
#                 "details": errors_list,
#             }
#         },
#     )


# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     """Handle all uncaught exceptions"""
#     logger.error(
#         f"Unhandled Exception: {type(exc).__name__} | "
#         f"Path: {request.url.path} | Error: {str(exc)}",
#         exc_info=True
#     )
    
#     # Show detailed error in development, generic in production
#     error_detail = str(exc) if ENVIRONMENT == "development" else "Internal server error"
    
#     return JSONResponse(
#         status_code=500,
#         content={
#             "success": False,
#             "error": {
#                 "message": error_detail,
#                 "type": type(exc).__name__,
#                 "status_code": 500,
#                 "path": str(request.url.path),
#             }
#         },
#     )


# # ============================================================================
# # REQUEST LOGGING MIDDLEWARE
# # ============================================================================
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     """Log all incoming requests and responses"""
#     logger.info(f"📨 {request.method} {request.url.path}")
    
#     try:
#         response = await call_next(request)
#         logger.info(
#             f"✅ {request.method} {request.url.path} | "
#             f"Status: {response.status_code}"
#         )
#         return response
#     except Exception as e:
#         logger.error(
#             f"❌ {request.method} {request.url.path} | Error: {str(e)}",
#             exc_info=True
#         )
#         raise


# # ============================================================================
# # ROOT & HEALTH CHECK ENDPOINTS
# # ============================================================================
# @app.get("/", tags=["Root"])
# async def root():
#     """Root endpoint - API information"""
#     return {
#         "success": True,
#         "message": "Welcome to SmartWork 360 API",
#         "data": {
#             "app_name": getattr(settings, 'APP_NAME', 'SmartWork 360'),
#             "description": "Government Productivity Management System",
#             "version": getattr(settings, 'VERSION', '1.0.0'),
#             "status": "running",
#             "environment": ENVIRONMENT,
#             "endpoints": {
#                 "docs": "/docs",
#                 "redoc": "/redoc",
#                 "openapi": "/openapi.json",
#                 "health": "/health",
#                 "ready": "/ready",
#                 "info": "/info",
#                 "api": "/api/v1",
#             },
#         },
#     }


# @app.get("/health", tags=["Health"])
# async def health_check():
#     """Health check endpoint with database status"""
#     db_status = "unknown"
#     db_error = None
    
#     try:
#         from sqlalchemy import text
#         with engine.connect() as conn:
#             conn.execute(text("SELECT 1"))
#         db_status = "healthy"
#     except Exception as e:
#         db_status = "unhealthy"
#         db_error = str(e)
#         logger.error(f"Health check DB error: {e}")
    
#     is_healthy = db_status == "healthy"
#     status_code = 200 if is_healthy else 503
    
#     return JSONResponse(
#         content={
#             "success": is_healthy,
#             "status": "healthy" if is_healthy else "unhealthy",
#             "data": {
#                 "app_name": getattr(settings, 'APP_NAME', 'SmartWork 360'),
#                 "version": getattr(settings, 'VERSION', '1.0.0'),
#                 "environment": ENVIRONMENT,
#                 "database": {
#                     "status": db_status,
#                     "error": db_error if not is_healthy else None,
#                 },
#             },
#         },
#         status_code=status_code,
#     )


# @app.get("/ready", tags=["Health"])
# async def readiness_check():
#     """Readiness probe for Kubernetes/container orchestration"""
#     try:
#         from sqlalchemy import text
#         with engine.connect() as conn:
#             conn.execute(text("SELECT 1"))
        
#         return {
#             "success": True,
#             "status": "ready",
#             "message": "Application is ready to receive traffic",
#         }
#     except Exception as e:
#         logger.error(f"Readiness check failed: {e}")
#         return JSONResponse(
#             status_code=503,
#             content={
#                 "success": False,
#                 "status": "not_ready",
#                 "message": "Application is not ready",
#                 "error": str(e) if ENVIRONMENT == "development" else "Service unavailable",
#             },
#         )


# @app.get("/info", tags=["Info"])
# async def api_info():
#     """Get API route information"""
#     routes = []
#     for route in app.routes:
#         if hasattr(route, "methods") and hasattr(route, "path"):
#             routes.append({
#                 "path": route.path,
#                 "methods": sorted(list(route.methods)),
#                 "name": route.name,
#                 "tags": getattr(route, "tags", [])
#             })
    
#     # Group routes by tag
#     routes_by_tag = {}
#     for route in routes:
#         tags = route.get("tags", ["Untagged"])
#         for tag in tags:
#             if tag not in routes_by_tag:
#                 routes_by_tag[tag] = []
#             routes_by_tag[tag].append({
#                 "path": route["path"],
#                 "methods": route["methods"]
#             })
    
#     return {
#         "success": True,
#         "data": {
#             "app_name": getattr(settings, 'APP_NAME', 'SmartWork 360'),
#             "version": getattr(settings, 'VERSION', '1.0.0'),
#             "environment": ENVIRONMENT,
#             "total_routes": len(routes),
#             "routes_by_tag": routes_by_tag,
#         }
#     }


# # ============================================================================
# # API ROUTERS - CORE
# # ============================================================================
# # Authentication routes (always required)
# from app.api.v1.endpoints import auth
# app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
# logger.info("✅ Authentication routes loaded")

# # Main application routes
# try:
#     from app.api.v1.endpoints import (
#         tasks,
#         analytics,
#         audit,
#         reports,
#         dashboard,
#     )
    
#     app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
#     app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
#     app.include_router(audit.router, prefix="/api/v1", tags=["Audit"])
#     app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
#     app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
    
#     logger.info("✅ Core API v1 routes loaded")
# except ImportError as e:
#     logger.warning(f"⚠️  Some v1 routes not available: {e}")


# # ============================================================================
# # API ROUTERS - OPTIONAL/ADVANCED FEATURES
# # ============================================================================
# # ML/AI routes (development only)
# if ENVIRONMENT == "development":
#     try:
#         from app.api import predictions, sentiment, assistant
        
#         app.include_router(predictions.router, prefix="/api", tags=["AI"])
#         app.include_router(sentiment.router, prefix="/api", tags=["AI"])
#         app.include_router(assistant.router, prefix="/api", tags=["AI"])
        
#         logger.info("✅ ML/AI routes loaded (development only)")
#     except ImportError as ml_error:
#         logger.warning(f"⚠️  ML/AI routes not available: {ml_error}")

# # Additional features (optional)
# try:
#     from app.api import (
#         blockchain,
#         notifications,
#         analytics_fraud,
#         access_analytics,
#         automation,
#         data_transfer,
#         dashboard_charts,
#     )
    
#     app.include_router(blockchain.router, prefix="/api", tags=["Blockchain"])
#     app.include_router(notifications.router, prefix="/api", tags=["Notifications"])
#     app.include_router(analytics_fraud.router, prefix="/api", tags=["Analytics"])
#     app.include_router(access_analytics.router, prefix="/api", tags=["Analytics"])
#     app.include_router(automation.router, prefix="/api", tags=["Automation"])
#     app.include_router(data_transfer.router, prefix="/api", tags=["Data"])
#     app.include_router(dashboard_charts.router, prefix="/api", tags=["Dashboard"])
    
#     logger.info("✅ Additional feature routes loaded")
# except ImportError as e:
#     logger.warning(f"⚠️  Some optional routes not available: {e}")


# # ============================================================================
# # MAIN ENTRY POINT (for direct script execution)
# # ============================================================================
# if __name__ == "__main__":
#     import uvicorn
    
#     # Configuration from environment
#     port = int(os.getenv("PORT", 8000))
#     host = os.getenv("HOST", "0.0.0.0")
#     reload = ENVIRONMENT == "development"
    
#     logger.info("=" * 60)
#     logger.info(f"🚀 Starting Uvicorn server")
#     logger.info(f"   Host: {host}")
#     logger.info(f"   Port: {port}")
#     logger.info(f"   Reload: {reload}")
#     logger.info(f"   Environment: {ENVIRONMENT}")
#     logger.info("=" * 60)
    
#     uvicorn.run(
#         "app.main:app",
#         host=host,
#         port=port,
#         reload=reload,
#         log_level="info",
#         access_log=True,
#     )





"""
SmartWork 360 - FastAPI Backend Application
Government Productivity Management System
"""
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


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
logger.info(f"🌍 Environment: {ENVIRONMENT}")


# ============================================================================
# APPLICATION LIFESPAN MANAGER
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events handler"""
    app_name = settings.APP_NAME
    version = settings.VERSION
    
    # Startup
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {app_name} v{version}")
    logger.info(f"📦 Environment: {ENVIRONMENT}")
    logger.info(f"🗄️  Database: {settings.DATABASE_URL[:40]}...")
    logger.info("=" * 60)
    
    try:
        # Import models to ensure they're registered
        from app.models import User, Task
        
        # Create tables in development (use Alembic in production)
        if ENVIRONMENT != "production":
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created/verified")
        else:
            logger.info("✅ Database tables management: Use Alembic migrations")
        
        # Test database connection
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)
        logger.warning("⚠️  Application will continue but database operations may fail")
    
    logger.info("=" * 60)
    logger.info("✅ Application startup complete")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 Application shutting down...")
    engine.dispose()
    logger.info("✅ Database connections closed")
    logger.info("👋 Application shutdown complete")
    logger.info("=" * 60)


# ============================================================================
# FASTAPI APPLICATION INITIALIZATION
# ============================================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="Government Productivity Management System - Backend API",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ============================================================================
# CORS CONFIGURATION
# ============================================================================
def get_allowed_origins():
    """Get list of allowed CORS origins based on environment"""
    # Start with settings CORS origins
    origins = settings.CORS_ORIGINS.copy()
    
    # Always add FRONTEND_URL
    if settings.FRONTEND_URL not in origins:
        origins.append(settings.FRONTEND_URL)
    
    # Add comma-separated ALLOWED_ORIGINS from environment
    allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
    if allowed_origins_env:
        extra_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
        for origin in extra_origins:
            if origin not in origins:
                origins.append(origin)
        logger.info(f"✅ Added ALLOWED_ORIGINS from env: {extra_origins}")
    
    # Development mode: allow additional localhost variations
    if ENVIRONMENT == "development":
        dev_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]
        for origin in dev_origins:
            if origin not in origins:
                origins.append(origin)
        logger.warning("⚠️  CORS: Development mode - allowing localhost origins")
    
    # Log all allowed origins
    logger.info(f"🔒 CORS allowed origins ({len(origins)} total):")
    for origin in origins:
        logger.info(f"   - {origin}")
    
    return origins


# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
logger.info("✅ CORS middleware configured")


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail} | "
        f"Path: {request.url.path} | Method: {request.method}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "method": request.method,
            },
        },
        headers=getattr(exc, 'headers', None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
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
    
    logger.warning(
        f"Validation Error: {request.url.path} | "
        f"Method: {request.method} | Errors: {len(errors_list)}"
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "message": "Validation error - please check your request data",
                "status_code": 422,
                "path": str(request.url.path),
                "details": errors_list,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(
        f"Unhandled Exception: {type(exc).__name__} | "
        f"Path: {request.url.path} | Error: {str(exc)}",
        exc_info=True
    )
    
    # Show detailed error in development, generic in production
    error_detail = str(exc) if ENVIRONMENT == "development" else "Internal server error"
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "message": error_detail,
                "type": type(exc).__name__,
                "status_code": 500,
                "path": str(request.url.path),
            }
        },
    )


# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses"""
    logger.info(f"📨 {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        logger.info(
            f"✅ {request.method} {request.url.path} | "
            f"Status: {response.status_code}"
        )
        return response
    except Exception as e:
        logger.error(
            f"❌ {request.method} {request.url.path} | Error: {str(e)}",
            exc_info=True
        )
        raise


# ============================================================================
# ROOT & HEALTH CHECK ENDPOINTS
# ============================================================================
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "success": True,
        "message": "Welcome to SmartWork 360 API",
        "data": {
            "app_name": settings.APP_NAME,
            "description": "Government Productivity Management System",
            "version": settings.VERSION,
            "status": "running",
            "environment": ENVIRONMENT,
            "endpoints": {
                "docs": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json",
                "health": "/health",
                "ready": "/ready",
                "info": "/info",
                "api": "/api/v1",
            },
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint with database status"""
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
        logger.error(f"Health check DB error: {e}")
    
    is_healthy = db_status == "healthy"
    status_code = 200 if is_healthy else 503
    
    return JSONResponse(
        content={
            "success": is_healthy,
            "status": "healthy" if is_healthy else "unhealthy",
            "data": {
                "app_name": settings.APP_NAME,
                "version": settings.VERSION,
                "environment": ENVIRONMENT,
                "database": {
                    "status": db_status,
                    "error": db_error if not is_healthy else None,
                },
            },
        },
        status_code=status_code,
    )


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe for Kubernetes/container orchestration"""
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
                "error": str(e) if ENVIRONMENT == "development" else "Service unavailable",
            },
        )


@app.get("/info", tags=["Info"])
async def api_info():
    """Get API route information"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": sorted(list(route.methods)),
                "name": route.name,
                "tags": getattr(route, "tags", [])
            })
    
    # Group routes by tag
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
            "environment": ENVIRONMENT,
            "total_routes": len(routes),
            "routes_by_tag": routes_by_tag,
        }
    }


# ============================================================================
# API ROUTERS - CORE
# ============================================================================
# Authentication routes (always required)
from app.api.v1.endpoints import auth
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
logger.info("✅ Authentication routes loaded")

# Main application routes
try:
    from app.api.v1.endpoints import (
        tasks,
        analytics,
        audit,
        reports,
        dashboard,
    )
    
    app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
    app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
    app.include_router(audit.router, prefix="/api/v1", tags=["Audit"])
    app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
    app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
    
    logger.info("✅ Core API v1 routes loaded")
except ImportError as e:
    logger.warning(f"⚠️  Some v1 routes not available: {e}")


# ============================================================================
# API ROUTERS - OPTIONAL/ADVANCED FEATURES
# ============================================================================
# ML/AI routes (development only)
if ENVIRONMENT == "development":
    try:
        from app.api import predictions, sentiment, assistant
        
        app.include_router(predictions.router, prefix="/api", tags=["AI"])
        app.include_router(sentiment.router, prefix="/api", tags=["AI"])
        app.include_router(assistant.router, prefix="/api", tags=["AI"])
        
        logger.info("✅ ML/AI routes loaded (development only)")
    except ImportError as ml_error:
        logger.warning(f"⚠️  ML/AI routes not available: {ml_error}")

# Additional features (optional)
try:
    from app.api import (
        blockchain,
        notifications,
        analytics_fraud,
        access_analytics,
        automation,
        data_transfer,
        dashboard_charts,
    )
    
    app.include_router(blockchain.router, prefix="/api", tags=["Blockchain"])
    app.include_router(notifications.router, prefix="/api", tags=["Notifications"])
    app.include_router(analytics_fraud.router, prefix="/api", tags=["Analytics"])
    app.include_router(access_analytics.router, prefix="/api", tags=["Analytics"])
    app.include_router(automation.router, prefix="/api", tags=["Automation"])
    app.include_router(data_transfer.router, prefix="/api", tags=["Data"])
    app.include_router(dashboard_charts.router, prefix="/api", tags=["Dashboard"])
    
    logger.info("✅ Additional feature routes loaded")
except ImportError as e:
    logger.warning(f"⚠️  Some optional routes not available: {e}")


# ============================================================================
# MAIN ENTRY POINT (for direct script execution)
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    
    # Configuration from environment
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = ENVIRONMENT == "development"
    
    logger.info("=" * 60)
    logger.info(f"🚀 Starting Uvicorn server")
    logger.info(f"   Host: {host}")
    logger.info(f"   Port: {port}")
    logger.info(f"   Reload: {reload}")
    logger.info(f"   Environment: {ENVIRONMENT}")
    logger.info("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True,
    )




