"""
Pydantic schemas for Task API request/response validation.

Defines schemas for creating, updating, and returning task data.
Enforces strict user isolation - user_id is never accepted from client.
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class TaskCreate(SQLModel):
    """
    Schema for creating a new task.

    Used in POST /tasks request body.
    Does not include user_id (comes from authenticated user),
    id, created_at, or updated_at (auto-generated).

    Security Note:
    - user_id is NOT accepted from client (prevents privilege escalation)
    - user_id is set from authenticated user in endpoint handler
    """
    title: str = Field(max_length=200, min_length=1, description="Task title (required)")
    description: Optional[str] = Field(default=None, max_length=2000, description="Detailed task description")
    priority: Optional[str] = Field(default=None, description="Task priority: low, medium, high")
    due_date: Optional[datetime] = Field(default=None, description="Task due date in ISO 8601 format")


class TaskUpdate(SQLModel):
    """
    Schema for updating an existing task (partial update).

    Used in PUT /tasks/{task_id} request body.
    All fields optional - only provided fields are updated.

    Security Note:
    - user_id is NOT accepted from client (prevents privilege escalation)
    - Ownership validation happens in endpoint handler
    """
    title: Optional[str] = Field(default=None, max_length=200, min_length=1, description="Task title")
    description: Optional[str] = Field(default=None, max_length=2000, description="Detailed task description")
    completed: Optional[bool] = Field(default=None, description="Task completion status")
    priority: Optional[str] = Field(default=None, description="Task priority: low, medium, high")
    due_date: Optional[datetime] = Field(default=None, description="Task due date in ISO 8601 format")


class TaskResponse(SQLModel):
    """
    Schema for task responses.

    Used in all API responses that return task data.
    Includes all fields including auto-generated ones and user_id.

    Security Note:
    - user_id is included in response for client reference
    - Client can verify task ownership
    """
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
