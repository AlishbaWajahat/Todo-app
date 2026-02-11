"""
Security utilities for password hashing and JWT token generation.

Provides bcrypt-based password hashing and JWT token creation for authentication.
"""
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from typing import Dict, Any
from .config import settings


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Bcrypt hashed password

    Security Notes:
    - Uses bcrypt with automatic salt generation
    - Cost factor: 12 rounds (default)
    - Hashes are one-way (cannot be reversed)
    - Each hash is unique due to random salt
    - Passwords truncated to 72 bytes (bcrypt limitation)

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> print(hashed)
        $2b$12$KIXxKj8N8avz5FvH8K9Ziu...
    """
    # Encode password to bytes and truncate to 72 bytes (bcrypt limitation)
    password_bytes = password.encode('utf-8')[:72]

    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password from database

    Returns:
        bool: True if password matches, False otherwise

    Security Notes:
    - Constant-time comparison (prevents timing attacks)
    - Automatically handles salt extraction from hash
    - Returns False for invalid hash format

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    try:
        # Encode password to bytes and truncate to 72 bytes
        password_bytes = plain_password.encode('utf-8')[:72]

        # Encode hash to bytes
        hash_bytes = hashed_password.encode('utf-8')

        # Verify password
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token with user data and expiration.

    Args:
        data: Dictionary of claims to include in token (typically {"sub": user_id, "email": email})
        expires_delta: Optional custom expiration time (default: 7 days)

    Returns:
        str: Encoded JWT token

    Security Notes:
    - Uses HS256 algorithm (symmetric signing)
    - Includes "exp" claim for expiration validation
    - Includes "iat" claim for issued-at timestamp
    - Secret key must match frontend/middleware configuration

    Token Claims:
    - sub: User ID (subject)
    - email: User email address
    - name: User display name (optional)
    - exp: Expiration timestamp (Unix epoch)
    - iat: Issued-at timestamp (Unix epoch)

    Example:
        >>> token = create_access_token({"sub": "user_123", "email": "user@example.com"})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = data.copy()

    # Set expiration time (default: 7 days)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    # Add standard JWT claims
    to_encode.update({
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow()  # Issued at time
    })

    # Encode token with secret key
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt
