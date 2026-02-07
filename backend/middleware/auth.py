"""
JWT Authentication Middleware.

Validates JWT tokens on every request, extracts user identity from the "sub" claim,
and stores user information in request.state for downstream access.

Security Features:
- Validates JWT signature using shared secret (must match Better Auth)
- Verifies token expiration (exp claim)
- Extracts user identity from "sub" claim (required)
- Logs authentication failures for security monitoring
- Returns 401 Unauthorized for invalid/missing tokens
- Automatically provisions users from JWT data on first authentication
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from typing import Dict, Optional, Any
import logging
from datetime import datetime

from core.config import settings
from core.database import engine
from models.user import User

# Configure structured logging for authentication events
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_or_create_user(session: Session, user_id: str, email: Optional[str] = None, name: Optional[str] = None) -> User:
    """
    Get existing user or create new user from JWT token data.

    Implements idempotent user provisioning using database UNIQUE constraint
    on user.id to handle race conditions gracefully.

    Flow:
    1. Attempt to fetch user by id from database
    2. If user exists, return it
    3. If user doesn't exist, create new user with JWT data
    4. If IntegrityError (race condition), rollback and fetch existing user

    Args:
        session: SQLModel database session
        user_id: User ID from JWT "sub" claim (required)
        email: User email from JWT "email" claim (optional)
        name: User display name from JWT "name" claim (optional)

    Returns:
        User: Existing or newly created user object

    Raises:
        Exception: If database operation fails (not IntegrityError)

    Security Notes:
    - User ID comes from validated JWT token (trusted source)
    - Database UNIQUE constraint on user.id prevents duplicates
    - Race conditions handled: concurrent requests create only one record
    - Minimal JWT data supported: only "sub" claim required

    Example Race Condition Handling:
    - Request 1 and Request 2 arrive simultaneously for new user
    - Both attempt INSERT
    - One succeeds, one fails with IntegrityError
    - Failed request rolls back and fetches existing user
    - Both requests proceed with same user record
    """
    # Attempt to fetch existing user
    existing_user = session.get(User, user_id)
    if existing_user:
        # User already exists, return it
        return existing_user

    # User doesn't exist, create new user
    try:
        new_user = User(
            id=user_id,
            email=email or f"{user_id}@unknown.local",  # Fallback email if not provided
            name=name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Log user provisioning event
        logger.info(f"User provisioned: user_id={user_id}, email={email or 'none'}")

        return new_user

    except IntegrityError:
        # Race condition: another request created the user
        # Rollback transaction and fetch existing user
        session.rollback()
        existing_user = session.get(User, user_id)

        if existing_user:
            logger.info(f"User already exists (race condition handled): user_id={user_id}")
            return existing_user
        else:
            # This should never happen, but handle it gracefully
            logger.critical(f"IntegrityError but user not found: user_id={user_id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to provision user: race condition handling failed"
            )


def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.

    Validates:
    - Token signature using JWT_SECRET
    - Token expiration (exp claim)
    - Token issued-at time (iat claim)

    Args:
        token: JWT token string from Authorization header

    Returns:
        dict: Decoded JWT payload with claims (sub, email, name, exp, iat)

    Raises:
        HTTPException: 401 if token is invalid, expired, or signature mismatch

    Security Notes:
    - Uses HS256 algorithm (symmetric signing)
    - JWT_SECRET must match Better Auth secret
    - Expired tokens are automatically rejected by python-jose
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={
                "verify_signature": True,  # Verify token signature
                "verify_exp": True,        # Verify expiration
                "verify_iat": True,        # Verify issued-at
            }
        )
        return payload
    except ExpiredSignatureError:
        # Token has expired
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError as e:
        # Token invalid, signature mismatch, or malformed
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def auth_middleware(request: Request, call_next):
    """
    Authentication middleware for FastAPI.

    Runs on every request to validate JWT tokens and extract user identity.

    Flow:
    1. Extract JWT token from Authorization: Bearer <token> header
    2. Validate token signature and expiration using decode_jwt()
    3. Extract user identity from "sub" claim (required)
    4. Store user info in request.state.user for downstream access
    5. Pass request to next middleware/route handler

    Bypass Rules:
    - OPTIONS requests bypass authentication (CORS preflight)
    - /health endpoint bypasses authentication (for monitoring)
    - /docs, /redoc, /openapi.json bypass authentication (API documentation)

    Error Handling:
    - Missing Authorization header → 401 "Authentication required"
    - Invalid/expired token → 401 "Invalid or expired token"
    - Missing "sub" claim → 401 "Invalid token format"
    - All failures logged with timestamp, IP, and error reason

    Args:
        request: FastAPI Request object
        call_next: Next middleware/route handler in chain

    Returns:
        Response from downstream handler or 401 error response

    Security Notes:
    - Stateless authentication (no server-side sessions)
    - User identity derived entirely from JWT token
    - Token must be present and valid on every request
    """
    # Allow OPTIONS requests (CORS preflight) without authentication
    if request.method == "OPTIONS":
        return await call_next(request)

    # Bypass authentication for health check, documentation, and auth endpoints
    bypass_paths = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/",  # Root endpoint
        "/api/v1/auth/signup",  # Public signup endpoint
        "/api/v1/auth/signin",  # Public signin endpoint
    ]

    if request.url.path in bypass_paths:
        return await call_next(request)

    # Allow public access to uploaded files (avatars)
    if request.url.path.startswith("/uploads/"):
        return await call_next(request)

    # Extract Authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        # Missing Authorization header
        client_ip = request.client.host if request.client else "unknown"
        logger.error(f"Authentication failed: Missing Authorization header (IP: {client_ip})")
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Authentication required",
                "code": "MISSING_TOKEN"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Validate Bearer token format
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        client_ip = request.client.host if request.client else "unknown"
        logger.error(f"Authentication failed: Invalid Authorization header format (IP: {client_ip})")
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Invalid Authorization header format. Expected: Bearer <token>",
                "code": "INVALID_AUTH_HEADER"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = parts[1]

    try:
        # Decode and validate JWT token
        payload = decode_jwt(token)

        # Extract user identity from "sub" claim (required)
        user_id = payload.get("sub")
        if not user_id:
            client_ip = request.client.host if request.client else "unknown"
            logger.error(f"Authentication failed: Missing 'sub' claim in token (IP: {client_ip})")
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid token format: missing user identifier",
                    "code": "MISSING_SUB_CLAIM"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Provision user from JWT data (lazy user creation)
        # This creates user record on first authentication
        try:
            with Session(engine) as session:
                user = get_or_create_user(
                    session=session,
                    user_id=user_id,
                    email=payload.get("email"),
                    name=payload.get("name")
                )

                # Store User object (not dict) in request.state for downstream access
                # This will be retrieved by get_current_user dependency
                request.state.user = user

        except Exception as e:
            # Database connection or provisioning failure
            client_ip = request.client.host if request.client else "unknown"
            logger.error(f"User provisioning failed: {str(e)} (IP: {client_ip}, user_id: {user_id})")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Failed to provision user profile",
                    "code": "USER_PROVISIONING_FAILED"
                }
            )

        # Pass request to next handler
        response = await call_next(request)
        return response

    except HTTPException as e:
        # JWT validation failed (expired, invalid signature, etc.)
        client_ip = request.client.host if request.client else "unknown"

        # Convert HTTPException detail to standard format
        if isinstance(e.detail, dict):
            # Detail is already a dict, use it directly
            content = e.detail
            log_message = e.detail.get("detail", str(e.detail))
        else:
            # Detail is a string, wrap it in standard format
            # Map common error messages to error codes
            error_code = "INVALID_TOKEN"
            if "expired" in str(e.detail).lower():
                error_code = "TOKEN_EXPIRED"

            content = {"detail": str(e.detail), "code": error_code}
            log_message = str(e.detail)

        logger.error(f"Authentication failed: {log_message} (IP: {client_ip})")
        return JSONResponse(
            status_code=e.status_code,
            content=content,
            headers=e.headers or {}
        )
    except Exception as e:
        # Unexpected error during authentication
        client_ip = request.client.host if request.client else "unknown"
        logger.error(f"Authentication error: {str(e)} (IP: {client_ip})")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error during authentication",
                "code": "AUTH_ERROR"
            }
        )
