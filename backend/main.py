"""
Task Management API - FastAPI Application Entry Point.

Provides RESTful CRUD operations for task management with persistent storage
in Neon Serverless PostgreSQL.

Security:
- JWT authentication required on all endpoints (except /health, /docs)
- User isolation enforced at query level
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import logging

from core.config import settings
from core.database import create_db_and_tables
from api.v1.endpoints import tasks, auth, users, agent
from middleware.auth import auth_middleware

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Implements defense-in-depth security controls:
    - HSTS: Force HTTPS for 1 year
    - X-Content-Type-Options: Prevent MIME sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS filter (legacy browsers)
    - Content-Security-Policy: Restrict resource loading
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Disable unnecessary browser features
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # HSTS: Force HTTPS for 1 year (only in production)
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS Protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    Creates database tables on startup.
    """
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: Cleanup (if needed)


# Initialize FastAPI application
app = FastAPI(
    title="Task Management API",
    description="RESTful API for managing tasks with persistent storage. Requires JWT authentication.",
    version="1.0.0",
    lifespan=lifespan
)


# Global exception handler for unhandled exceptions
# Prevents stack trace leakage to clients while logging full details
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for all unhandled exceptions.

    Catches any exception not handled by route handlers and returns
    a generic 500 error to prevent information leakage.

    Security:
    - Does NOT expose stack traces to clients
    - Logs full error details for debugging
    - Returns generic error message

    Args:
        request: FastAPI Request object
        exc: Unhandled exception

    Returns:
        JSONResponse: 500 error with generic message
    """
    # Log full error details for debugging (includes stack trace)
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        exc_info=True,  # Include stack trace in logs
        extra={
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )

    # Return generic error to client (no sensitive information)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "code": "INTERNAL_SERVER_ERROR"
        }
    )


# Configure CORS middleware (must be added before auth middleware)
# Restricts to only required methods and headers for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],  # Explicit methods only
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With"
    ],  # Explicit headers only
    max_age=600,  # Cache preflight for 10 minutes
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)


# Register authentication middleware
# This runs on every request to validate JWT tokens
# Bypasses: /health, /docs, /redoc, /openapi.json
@app.middleware("http")
async def authentication_middleware(request, call_next):
    """
    Global authentication middleware.

    Validates JWT tokens on all requests except health check and docs.
    """
    return await auth_middleware(request, call_next)


# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")

# Mount static files for uploaded avatars
# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/", tags=["root"])
def root():
    """
    Root endpoint - API information.

    Returns:
        dict: API information and status
    """
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "status": "operational",
        "authentication": "JWT required (except /health)"
    }


@app.get("/health", tags=["monitoring"])
def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    This endpoint bypasses authentication to allow external monitoring
    services to check API availability without requiring credentials.

    Returns:
        dict: Health status information

    Security Notes:
    - Does NOT require authentication (bypassed in middleware)
    - Should only return non-sensitive operational status
    - Used by monitoring tools, load balancers, and orchestration platforms
    """
    return {
        "status": "healthy",
        "service": "task-management-api",
        "version": "1.0.0"
    }
