"""
Message entity model for database operations.

Defines the Message table structure using SQLModel for individual chat messages.
"""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Enum as SQLEnum, UniqueConstraint
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from uuid import UUID

if TYPE_CHECKING:
    from .conversation import Conversation
    from .tool_call import ToolCall


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(SQLModel, table=True):
    """
    Message entity - represents a single message within a conversation.

    Messages are ordered by sequence_number within each conversation.
    Each message can have associated tool calls.

    Attributes:
        id: Auto-incrementing message ID (primary key)
        conversation_id: Parent conversation (UUID FK to conversations.id, required)
        role: Message role (user, assistant, system)
        content: Message text content (required)
        sequence_number: Order within conversation (0-indexed, required)
        created_at: When message was created (UTC timestamp)
        model: AI model used (optional, e.g., "gemini-2.5-flash", max 100 chars)
        tokens_used: Token count for analytics (optional, must be >= 0)
    """
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("conversation_id", "sequence_number", name="unique_conversation_sequence"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: MessageRole = Field(sa_column=Column(SQLEnum(MessageRole), nullable=False))
    content: str = Field(nullable=False)
    sequence_number: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Optional metadata
    model: Optional[str] = Field(default=None, max_length=100)
    tokens_used: Optional[int] = Field(default=None, ge=0)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    tool_calls: List["ToolCall"] = Relationship(
        back_populates="message",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
