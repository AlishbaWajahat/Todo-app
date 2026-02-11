"""
User request and response schemas for API endpoints.

Defines Pydantic models for validating user input and serializing User data.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserSignupRequest(BaseModel):
    """
    User signup request schema.

    Validates user registration data with email, password, and optional name.

    Attributes:
        email: User email address (must be valid email format)
        password: User password (minimum 8 characters)
        name: User display name (optional)
    """
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    name: Optional[str] = Field(None, max_length=100, description="User display name")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserSigninRequest(BaseModel):
    """
    User signin request schema.

    Validates user login credentials.

    Attributes:
        email: User email address
        password: User password
    """
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    """
    User profile update request schema.

    Allows updating user's display name only.
    Email cannot be changed for security reasons.

    Attributes:
        name: New display name (optional)
    """
    name: Optional[str] = Field(None, max_length=100, description="User display name")


class UserResponse(BaseModel):
    """
    User response schema for API endpoints.

    Used to serialize User model data in API responses.
    Excludes password_hash for security.

    Attributes:
        id: User ID (UUID string)
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


class AuthResponse(BaseModel):
    """
    Authentication response schema.

    Returned after successful signup or signin.
    Includes user data and JWT access token.

    Attributes:
        user: User profile data
        token: JWT access token for authentication
    """
    user: UserResponse
    token: str
