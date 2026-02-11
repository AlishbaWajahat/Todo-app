"""
Conversation entity model for database operations.

Defines the Conversation table structure using SQLModel for chat history persistence.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation entity - represents a chat session between a user and the AI agent.

    Each conversation belongs to a single user and contains multiple messages.
    Conversations are identified by UUID to prevent enumeration attacks.

    Attributes:
        id: Unique conversation identifier (UUID, auto-generated)
        user_id: Owner of the conversation (string FK to users.id, required)
        title: Conversation title (optional, auto-generated from first message, max 255 chars)
        created_at: When conversation was created (UTC timestamp)
        updated_at: Last message timestamp (UTC timestamp)
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
