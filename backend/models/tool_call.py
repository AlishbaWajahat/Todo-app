"""
ToolCall entity model for database operations.

Defines the ToolCall table structure using SQLModel for tracking MCP tool executions.
"""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Enum as SQLEnum, JSON
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .message import Message


class ToolCallStatus(str, Enum):
    """Tool call execution status."""
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class ToolCall(SQLModel, table=True):
    """
    ToolCall entity - records execution of MCP tools triggered by agent during conversation.

    Records tool invocations, inputs, outputs, and execution status.
    Enables debugging and analytics for agent behavior.

    Attributes:
        id: Auto-incrementing tool call ID (primary key)
        message_id: Associated message (int FK to messages.id, required)
        tool_name: Name of MCP tool (required, max 100 chars, e.g., "add_task", "list_tasks")
        tool_input: Tool input parameters (JSONB, required)
        tool_output: Tool execution result (JSONB, optional)
        status: Execution status (pending, success, error)
        error_message: Error details if status=error (optional)
        execution_time_ms: Execution duration in milliseconds (optional, must be >= 0)
        created_at: When tool was invoked (UTC timestamp)
        completed_at: When tool execution finished (optional, UTC timestamp)
    """
    __tablename__ = "tool_calls"

    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="messages.id", nullable=False, index=True)
    tool_name: str = Field(nullable=False, max_length=100, index=True)
    tool_input: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    tool_output: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON), default=None)
    status: ToolCallStatus = Field(sa_column=Column(SQLEnum(ToolCallStatus), nullable=False))
    error_message: Optional[str] = Field(default=None)
    execution_time_ms: Optional[int] = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    message: Optional["Message"] = Relationship(back_populates="tool_calls")
