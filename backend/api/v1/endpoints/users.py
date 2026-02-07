"""
User profile management endpoints.

Provides RESTful API endpoints for viewing and updating user profiles.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session
from datetime import datetime
import logging
import os
from pathlib import Path
import uuid

from core.database import get_session
from dependencies.auth import get_current_user
from models.user import User
from schemas.user import UserResponse, UserUpdateRequest

# Configure logging
logger = logging.getLogger(__name__)

# Create router with tags for API documentation
router = APIRouter()

# Avatar upload configuration
UPLOAD_DIR = Path("uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Get the authenticated user's profile information.",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "user_123abc",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "avatar_url": "https://example.com/avatars/user_123abc.jpg",
                        "created_at": "2026-02-06T10:30:00Z",
                        "updated_at": "2026-02-06T10:30:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Authentication required",
                        "code": "UNAUTHORIZED"
                    }
                }
            }
        }
    }
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user profile.

    Returns the authenticated user's profile information.
    User is identified from JWT token in Authorization header.

    Args:
        current_user: Authenticated user (injected from JWT token)

    Returns:
        UserResponse: User profile data (excludes password_hash)

    Security Notes:
    - Requires valid JWT token in Authorization header
    - Only returns data for authenticated user
    - Password hash never included in response
    """
    logger.info(f"User profile retrieved: {current_user.id}")
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Update the authenticated user's profile information (name only).",
    responses={
        200: {
            "description": "Profile updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "user_123abc",
                        "email": "user@example.com",
                        "name": "Jane Doe",
                        "avatar_url": "https://example.com/avatars/user_123abc.jpg",
                        "created_at": "2026-02-06T10:30:00Z",
                        "updated_at": "2026-02-06T16:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required"
        }
    }
)
def update_current_user_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> UserResponse:
    """
    Update current user profile.

    Updates the authenticated user's profile information.
    Currently only supports updating the display name.
    Email cannot be changed for security reasons.

    Args:
        update_data: Profile update data (name)
        current_user: Authenticated user (injected from JWT token)
        session: Database session (injected)

    Returns:
        UserResponse: Updated user profile

    Security Notes:
    - Requires valid JWT token in Authorization header
    - User can only update their own profile
    - Email changes not allowed (prevents account takeover)
    """
    # Update name if provided
    if update_data.name is not None:
        current_user.name = update_data.name

    # Update timestamp
    current_user.updated_at = datetime.utcnow()

    # Save to database
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    logger.info(f"User profile updated: {current_user.id}")

    return UserResponse.model_validate(current_user)


@router.post(
    "/me/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload user avatar",
    description="Upload a new profile picture for the authenticated user.",
    responses={
        200: {
            "description": "Avatar uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "user_123abc",
                        "email": "user@example.com",
                        "name": "Jane Doe",
                        "avatar_url": "/uploads/avatars/user_123abc_abc123.jpg",
                        "created_at": "2026-02-06T10:30:00Z",
                        "updated_at": "2026-02-06T16:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid file",
            "content": {
                "application/json": {
                    "examples": {
                        "file_too_large": {
                            "value": {
                                "detail": "File size exceeds 5MB limit",
                                "code": "FILE_TOO_LARGE"
                            }
                        },
                        "invalid_format": {
                            "value": {
                                "detail": "Invalid file format. Allowed: jpg, jpeg, png, gif",
                                "code": "INVALID_FILE_FORMAT"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required"
        }
    }
)
async def upload_avatar(
    avatar: UploadFile = File(..., description="Avatar image file (JPEG, PNG, GIF, max 5MB)"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> UserResponse:
    """
    Upload user avatar.

    Uploads a new profile picture for the authenticated user.
    Validates file size and format before saving.

    Args:
        avatar: Uploaded image file
        current_user: Authenticated user (injected from JWT token)
        session: Database session (injected)

    Returns:
        UserResponse: Updated user profile with new avatar_url

    Raises:
        HTTPException 400: File too large or invalid format

    Security Notes:
    - Requires valid JWT token in Authorization header
    - File size limited to 5MB
    - Only image formats allowed (jpg, jpeg, png, gif)
    - Files saved with unique names to prevent overwrites
    - User can only upload avatar for their own profile
    """
    # Validate file extension
    file_ext = Path(avatar.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Avatar upload failed: Invalid format - {file_ext}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            headers={"X-Error-Code": "INVALID_FILE_FORMAT"}
        )

    # Read file content
    file_content = await avatar.read()

    # Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        logger.warning(f"Avatar upload failed: File too large - {len(file_content)} bytes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit",
            headers={"X-Error-Code": "FILE_TOO_LARGE"}
        )

    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{current_user.id}_{unique_id}{file_ext}"
    file_path = UPLOAD_DIR / filename

    # Save file to disk
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        logger.error(f"Avatar upload failed: Failed to save file - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save avatar file",
            headers={"X-Error-Code": "FILE_SAVE_FAILED"}
        )

    # Update user avatar_url
    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    current_user.updated_at = datetime.utcnow()

    # Save to database
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    logger.info(f"Avatar uploaded successfully: {current_user.id} - {filename}")

    return UserResponse.model_validate(current_user)
