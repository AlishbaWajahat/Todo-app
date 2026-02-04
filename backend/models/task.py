"""
Task entity model for database operations.

Defines the Task table structure using SQLModel with validation rules.
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Task(SQLModel, table=True):
    """
    Task entity - represents a todo item belonging to a specific user.

    This model is used for database operations and includes all fields
    that are persisted to PostgreSQL. Updated to support multi-user functionality
    with user_id foreign key for strict data isolation.

    Attributes:
        id: Unique identifier (auto-generated)
        user_id: Owner of the task (string FK to users.id, required)
        title: Task title/summary (required, 1-200 chars)
        description: Detailed task description (optional, max 1000 chars)
        completed: Completion status (default: False)
        priority: Task priority (optional: low, medium, high)
        due_date: Task due date (optional)
        created_at: When task was created (UTC timestamp)
        updated_at: When task was last modified (UTC timestamp)
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    priority: Optional[str] = Field(default=None, max_length=20)
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
