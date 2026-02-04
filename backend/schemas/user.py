"""
User response schemas for API endpoints.

Defines Pydantic models for serializing User data in API responses.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """
    User response schema for API endpoints.

    Used to serialize User model data in API responses.
    Includes all user fields for client consumption.

    Attributes:
        id: User ID (from JWT "sub" claim)
        email: User email address
        name: User display name (optional)
        avatar_url: User profile picture URL (optional)
        created_at: When user record was created
        updated_at: When user record was last updated
    """
    id: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
