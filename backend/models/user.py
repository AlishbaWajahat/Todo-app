"""
User entity model for database operations.

Defines the User table structure using SQLModel for authentication.
Supports both native authentication (email/password) and JWT-based auto-provisioning.
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class User(SQLModel, table=True):
    """
    User entity - represents an authenticated user in the system.

    Supports two authentication modes:
    1. Native: Users sign up with email/password, password_hash is stored
    2. JWT-based: Users are auto-provisioned from external JWT tokens

    Attributes:
        id: User ID (UUID string, auto-generated for native auth or from JWT "sub" claim)
        email: User email address (unique, indexed)
        password_hash: Hashed password (bcrypt, optional for JWT-based users)
        name: User display name (optional)
        avatar_url: User profile picture URL (optional)
        created_at: When user record was created (UTC timestamp)
        updated_at: When user record was last updated (UTC timestamp)
    """
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: Optional[str] = None  # Only for native authentication
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
