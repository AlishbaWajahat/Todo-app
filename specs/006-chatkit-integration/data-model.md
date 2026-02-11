# Data Model: ChatKit UI & End-to-End Integration

**Feature**: 006-chatkit-integration
**Date**: 2026-02-09
**Status**: Draft

## Overview

This document defines the data models for conversation persistence in the ChatKit integration. All models use SQLModel (SQLAlchemy + Pydantic) for type safety and database operations.

---

## Entity 1: Conversation

**Purpose**: Represents a chat session between a user and the AI agent.

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    """
    Conversation model for chat history persistence.

    Each conversation belongs to a single user and contains multiple messages.
    Conversations are identified by UUID to prevent enumeration attacks.
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

**Fields**:
- `id` (UUID, PK): Unique conversation identifier
- `user_id` (int, FK): Owner of the conversation (references users.id)
- `title` (str, optional): Conversation title (auto-generated from first message)
- `created_at` (datetime): When conversation was created
- `updated_at` (datetime): Last message timestamp (updated via trigger or application logic)

**Relationships**:
- `user`: Many-to-one with User model
- `messages`: One-to-many with Message model (cascade delete)

**Indexes**:
- `user_id`: For filtering user's conversations
- `(user_id, updated_at)`: For sorting user's conversations by recency

**Validation Rules**:
- `user_id` must reference existing user
- `title` max length 255 characters
- `created_at` and `updated_at` must be valid timestamps

**State Transitions**: None (conversations don't have state)

---

## Entity 2: Message

**Purpose**: Represents a single message within a conversation (user or assistant).

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLEnum
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(SQLModel, table=True):
    """
    Message model for individual chat messages.

    Messages are ordered by sequence_number within each conversation.
    Each message can have associated tool calls.
    """
    __tablename__ = "messages"

    id: int = Field(default=None, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: MessageRole = Field(sa_column=Column(SQLEnum(MessageRole)), nullable=False)
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

    class Config:
        # Ensure unique sequence numbers within conversation
        table_args = (
            UniqueConstraint("conversation_id", "sequence_number", name="unique_conversation_sequence"),
        )
```

**Fields**:
- `id` (int, PK): Auto-incrementing message ID
- `conversation_id` (UUID, FK): Parent conversation
- `role` (enum): Message role (user, assistant, system)
- `content` (text): Message text content
- `sequence_number` (int): Order within conversation (0-indexed)
- `created_at` (datetime): When message was created
- `model` (str, optional): AI model used (e.g., "gemini-2.5-flash")
- `tokens_used` (int, optional): Token count for analytics

**Relationships**:
- `conversation`: Many-to-one with Conversation model
- `tool_calls`: One-to-many with ToolCall model (cascade delete)

**Indexes**:
- `conversation_id`: For loading conversation history
- `(conversation_id, sequence_number)`: For ordered retrieval

**Validation Rules**:
- `conversation_id` must reference existing conversation
- `role` must be one of: user, assistant, system
- `content` cannot be empty
- `sequence_number` must be unique within conversation
- `sequence_number` must be >= 0
- `tokens_used` must be >= 0 if provided

**State Transitions**: None (messages are immutable once created)

---

## Entity 3: ToolCall

**Purpose**: Records execution of MCP tools triggered by agent during conversation.

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLEnum
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import JSON

class ToolCallStatus(str, Enum):
    """Tool call execution status."""
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"

class ToolCall(SQLModel, table=True):
    """
    Tool call model for tracking MCP tool executions.

    Records tool invocations, inputs, outputs, and execution status.
    Enables debugging and analytics for agent behavior.
    """
    __tablename__ = "tool_calls"

    id: int = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="messages.id", nullable=False, index=True)
    tool_name: str = Field(nullable=False, max_length=100, index=True)
    tool_input: Dict[str, Any] = Field(sa_column=Column(JSON), nullable=False)
    tool_output: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON), default=None)
    status: ToolCallStatus = Field(sa_column=Column(SQLEnum(ToolCallStatus)), nullable=False)
    error_message: Optional[str] = Field(default=None)
    execution_time_ms: Optional[int] = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    message: Optional["Message"] = Relationship(back_populates="tool_calls")
```

**Fields**:
- `id` (int, PK): Auto-incrementing tool call ID
- `message_id` (int, FK): Associated message (assistant message that triggered tool)
- `tool_name` (str): Name of MCP tool (e.g., "add_task", "list_tasks")
- `tool_input` (JSONB): Tool input parameters
- `tool_output` (JSONB, optional): Tool execution result
- `status` (enum): Execution status (pending, success, error)
- `error_message` (text, optional): Error details if status=error
- `execution_time_ms` (int, optional): Execution duration in milliseconds
- `created_at` (datetime): When tool was invoked
- `completed_at` (datetime, optional): When tool execution finished

**Relationships**:
- `message`: Many-to-one with Message model

**Indexes**:
- `message_id`: For loading tool calls with message
- `tool_name`: For analytics on tool usage

**Validation Rules**:
- `message_id` must reference existing message
- `tool_name` must be one of: add_task, list_tasks, complete_task, update_task, delete_task
- `tool_input` must be valid JSON
- `tool_output` must be valid JSON if provided
- `status` must be one of: pending, success, error
- `execution_time_ms` must be >= 0 if provided
- `completed_at` must be >= `created_at` if provided

**State Transitions**:
```
pending → success (tool executed successfully)
pending → error (tool execution failed)
```

---

## Relationships Diagram

```
User (existing)
  ↓ (1:N)
Conversation
  ↓ (1:N)
Message
  ↓ (1:N)
ToolCall
```

**Cascade Behavior**:
- Delete User → Delete all Conversations → Delete all Messages → Delete all ToolCalls
- Delete Conversation → Delete all Messages → Delete all ToolCalls
- Delete Message → Delete all ToolCalls

---

## Database Constraints

**Primary Keys**:
- `conversations.id`: UUID
- `messages.id`: BIGSERIAL (auto-increment)
- `tool_calls.id`: BIGSERIAL (auto-increment)

**Foreign Keys**:
- `conversations.user_id` → `users.id` (ON DELETE CASCADE)
- `messages.conversation_id` → `conversations.id` (ON DELETE CASCADE)
- `tool_calls.message_id` → `messages.id` (ON DELETE CASCADE)

**Unique Constraints**:
- `(messages.conversation_id, messages.sequence_number)`: Prevent duplicate sequence numbers

**Check Constraints**:
- `messages.sequence_number >= 0`: Sequence numbers must be non-negative
- `messages.tokens_used >= 0`: Token count must be non-negative
- `tool_calls.execution_time_ms >= 0`: Execution time must be non-negative
- `tool_calls.completed_at >= tool_calls.created_at`: Completion time must be after creation

**Indexes** (for performance):
- `idx_conversations_user_id` ON `conversations(user_id)`
- `idx_conversations_user_updated` ON `conversations(user_id, updated_at DESC)`
- `idx_messages_conversation_sequence` ON `messages(conversation_id, sequence_number)`
- `idx_tool_calls_message_id` ON `tool_calls(message_id)`
- `idx_tool_calls_tool_name` ON `tool_calls(tool_name)`

---

## Migration Strategy

**Alembic Migration**:
```python
# alembic/versions/[timestamp]_add_conversation_tables.py

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_user_updated', 'conversations', ['user_id', 'updated_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', 'system', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('conversation_id', 'sequence_number', name='unique_conversation_sequence'),
        sa.CheckConstraint('sequence_number >= 0', name='check_sequence_positive'),
        sa.CheckConstraint('tokens_used IS NULL OR tokens_used >= 0', name='check_tokens_positive'),
    )
    op.create_index('idx_messages_conversation_sequence', 'messages', ['conversation_id', 'sequence_number'])

    # Create tool_calls table
    op.create_table(
        'tool_calls',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('message_id', sa.BigInteger(), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('tool_input', postgresql.JSONB(), nullable=False),
        sa.Column('tool_output', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'success', 'error', name='toolcallstatus'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.CheckConstraint('execution_time_ms IS NULL OR execution_time_ms >= 0', name='check_execution_time_positive'),
        sa.CheckConstraint('completed_at IS NULL OR completed_at >= created_at', name='check_completion_time'),
    )
    op.create_index('idx_tool_calls_message_id', 'tool_calls', ['message_id'])
    op.create_index('idx_tool_calls_tool_name', 'tool_calls', ['tool_name'])

def downgrade():
    op.drop_table('tool_calls')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.execute('DROP TYPE IF EXISTS toolcallstatus')
    op.execute('DROP TYPE IF EXISTS messagerole')
```

---

## Query Patterns

**Get User's Conversations (sorted by recent)**:
```python
conversations = session.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
).all()
```

**Get Conversation History (with messages and tool calls)**:
```python
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.sequence_number)
    .options(selectinload(Message.tool_calls))
).all()
```

**Create New Message with Tool Call**:
```python
# Create message
message = Message(
    conversation_id=conversation_id,
    role=MessageRole.ASSISTANT,
    content="Task created successfully",
    sequence_number=next_sequence,
    model="gemini-2.5-flash"
)
session.add(message)
session.flush()  # Get message.id

# Create tool call
tool_call = ToolCall(
    message_id=message.id,
    tool_name="add_task",
    tool_input={"user_id": "123", "title": "Buy groceries"},
    tool_output={"success": True, "data": {"id": 456}},
    status=ToolCallStatus.SUCCESS,
    execution_time_ms=150
)
session.add(tool_call)
session.commit()
```

---

## Data Model Summary

| Entity | Purpose | Key Fields | Relationships |
|--------|---------|------------|---------------|
| **Conversation** | Chat session | id (UUID), user_id, title, timestamps | User (N:1), Messages (1:N) |
| **Message** | Individual message | id, conversation_id, role, content, sequence_number | Conversation (N:1), ToolCalls (1:N) |
| **ToolCall** | Tool execution record | id, message_id, tool_name, input/output (JSONB), status | Message (N:1) |

**Total New Tables**: 3
**Total New Indexes**: 6
**Total New Constraints**: 7 (FK + unique + check)

---

**Status**: Ready for implementation via Alembic migration and SQLModel integration.
