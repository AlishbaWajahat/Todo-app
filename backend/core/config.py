"""
Configuration management using Pydantic Settings.

Loads environment variables from .env file and provides type-safe configuration.
"""
from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        database_url: PostgreSQL connection string for Neon database
        jwt_secret: Secret key for JWT token verification (must match Better Auth)
        jwt_algorithm: JWT signing algorithm (default: HS256)
        cors_origins: List of allowed CORS origins for frontend
        environment: Application environment (development, production, test)
    """
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    cors_origins: List[str] = ["http://localhost:3000"]
    environment: str = "development"

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate that JWT_SECRET is set and meets minimum security requirements."""
        if not v or v.strip() == "":
            raise ValueError("JWT_SECRET must be set in environment variables")
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters for security")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()
