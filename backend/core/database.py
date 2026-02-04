"""
Database connection and session management for Neon Serverless PostgreSQL.

Configures SQLModel engine with connection pooling optimized for serverless architecture.
"""
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import logging

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine with connection pooling for Neon
engine = create_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL query logging in development
    pool_pre_ping=True,  # Verify connections before use (handles serverless cold starts)
    pool_size=5,  # Base connection pool size
    max_overflow=10,  # Maximum overflow connections (total max: 15)
    pool_recycle=3600,  # Recycle connections after 1 hour
)


def create_db_and_tables():
    """
    Create all database tables defined in SQLModel models.

    This should be called once during application startup.
    Uses SQLModel.metadata.create_all() to create tables if they don't exist.

    IMPORTANT: Models must be imported before calling this function
    so SQLModel knows about them.
    """
    try:
        # Import models here to ensure they're registered with SQLModel
        from models.task import Task  # noqa: F401
        from models.user import User  # noqa: F401

        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Yields:
        Session: SQLModel database session

    Usage:
        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            # Use session here
            pass

    The session is automatically closed after the request completes.
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
