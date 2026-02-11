"""
Authentication endpoints for user signup and signin.

Provides RESTful API endpoints for user registration and authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
import logging

from core.database import get_session
from core.security import hash_password, verify_password, create_access_token
from models.user import User
from schemas.user import UserSignupRequest, UserSigninRequest, AuthResponse, UserResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router with tags for API documentation
router = APIRouter()


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up a new user",
    description="Create a new user account with email and password. Returns user profile and JWT token.",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "user_123abc",
                            "email": "user@example.com",
                            "name": "John Doe",
                            "avatar_url": None,
                            "created_at": "2026-02-06T10:30:00Z",
                            "updated_at": "2026-02-06T10:30:00Z"
                        },
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        },
        400: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Email already registered",
                        "code": "EMAIL_EXISTS"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Password must be at least 8 characters",
                        "code": "VALIDATION_ERROR"
                    }
                }
            }
        }
    }
)
def signup(
    user_data: UserSignupRequest,
    session: Session = Depends(get_session)
) -> AuthResponse:
    """
    Sign up a new user.

    Creates a new user account with email and password authentication.
    Hashes password with bcrypt before storing in database.
    Generates JWT token for immediate authentication.

    Args:
        user_data: User signup data (email, password, name)
        session: Database session (injected)

    Returns:
        AuthResponse: User profile and JWT access token

    Raises:
        HTTPException 400: Email already registered
        HTTPException 422: Validation error (invalid email, short password)

    Security Notes:
    - Password is hashed with bcrypt before storage
    - Email uniqueness enforced by database constraint
    - JWT token valid for 7 days (default)
    - Password never returned in response
    """
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        logger.warning(f"Signup failed: Email already registered - {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
            headers={"X-Error-Code": "EMAIL_EXISTS"}
        )

    # Hash password
    password_hash = hash_password(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        name=user_data.name,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Save to database
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    logger.info(f"User created successfully: {new_user.id} - {new_user.email}")

    # Generate JWT token
    token = create_access_token(
        data={
            "sub": new_user.id,
            "email": new_user.email,
            "name": new_user.name
        }
    )

    # Return user and token
    return AuthResponse(
        user=UserResponse.model_validate(new_user),
        token=token
    )


@router.post(
    "/signin",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in an existing user",
    description="Authenticate user with email and password. Returns user profile and JWT token.",
    responses={
        200: {
            "description": "Authentication successful",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "user_123abc",
                            "email": "user@example.com",
                            "name": "John Doe",
                            "avatar_url": "https://example.com/avatars/user_123abc.jpg",
                            "created_at": "2026-02-06T10:30:00Z",
                            "updated_at": "2026-02-06T10:30:00Z"
                        },
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid email or password",
                        "code": "INVALID_CREDENTIALS"
                    }
                }
            }
        }
    }
)
def signin(
    credentials: UserSigninRequest,
    session: Session = Depends(get_session)
) -> AuthResponse:
    """
    Sign in an existing user.

    Authenticates user with email and password.
    Verifies password hash and generates new JWT token.

    Args:
        credentials: User signin credentials (email, password)
        session: Database session (injected)

    Returns:
        AuthResponse: User profile and JWT access token

    Raises:
        HTTPException 401: Invalid email or password

    Security Notes:
    - Uses constant-time password comparison (prevents timing attacks)
    - Returns generic error message (doesn't reveal if email exists)
    - Generates new JWT token on each signin
    - Password never returned in response
    """
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    # Verify user exists and password is correct
    if not user or not user.password_hash:
        logger.warning(f"Signin failed: User not found - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"X-Error-Code": "INVALID_CREDENTIALS"}
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Signin failed: Invalid password - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"X-Error-Code": "INVALID_CREDENTIALS"}
        )

    logger.info(f"User signed in successfully: {user.id} - {user.email}")

    # Generate JWT token
    token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "name": user.name
        }
    )

    # Return user and token
    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token
    )
