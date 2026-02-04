"""
User entity model for database operations.

Defines the User table structure using SQLModel for JWT-based authentication.
Users are automatically provisioned from JWT token data on first authentication.
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """
    User entity - represents an authenticated user in the system.

    Users are automatically created from JWT token data on first authentication.
    The user ID comes from the JWT "sub" claim (typically a UUID or auth provider ID).

    Attributes:
        id: User ID from JWT "sub" claim (string, not auto-generated)
        email: User email address from JWT "email" claim (unique)
        name: User display name from JWT "name" claim (optional)
        avatar_url: User profile picture URL (optional, reserved for future use)
        created_at: When user record was created (UTC timestamp)
        updated_at: When user record was last updated (UTC timestamp)
    """
    __tablename__ = "users"

    id: str = Field(primary_key=True)  # From JWT "sub" claim
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
