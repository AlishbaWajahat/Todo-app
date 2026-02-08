"""Input schemas for MCP task management tools.

This module defines Pydantic input schemas for all 5 MCP tools,
ensuring proper validation and type safety.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""
    user_id: str = Field(..., description="Authenticated user ID (required)", min_length=1)
    completed: Optional[bool] = Field(None, description="Filter by completion status (optional)")
    priority: Optional[str] = Field(None, description="Filter by priority: low, medium, high (optional)")

    class Config:
        json_schema_extra = {
            "examples": [
                {"user_id": "user123", "completed": None, "priority": None},
                {"user_id": "user123", "completed": True, "priority": "high"}
            ]
        }


class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""
    user_id: str = Field(..., description="Authenticated user ID (required)", min_length=1)
    title: str = Field(..., description="Task title (required)", min_length=1, max_length=500)
    description: Optional[str] = Field(None, description="Task description (optional)", max_length=2000)
    priority: Optional[str] = Field(None, description="Task priority: low, medium, high (optional)")
    due_date: Optional[datetime] = Field(None, description="Task due date in ISO 8601 format (optional)")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "user_id": "user123",
                    "title": "Buy milk",
                    "description": "Get 2% milk from store",
                    "priority": "medium",
                    "due_date": "2026-02-10T10:00:00Z"
                },
                {
                    "user_id": "user123",
                    "title": "Call dentist",
                    "description": None,
                    "priority": None,
                    "due_date": None
                }
            ]
        }


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""
    user_id: str = Field(..., description="Authenticated user ID (required)", min_length=1)
    task_id: int = Field(..., description="Task ID to update (required)", gt=0)
    completed: bool = Field(..., description="New completion status (required)")

    class Config:
        json_schema_extra = {
            "examples": [
                {"user_id": "user123", "task_id": 1, "completed": True},
                {"user_id": "user123", "task_id": 2, "completed": False}
            ]
        }


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    user_id: str = Field(..., description="Authenticated user ID (required)", min_length=1)
    task_id: int = Field(..., description="Task ID to update (required)", gt=0)
    new_title: Optional[str] = Field(None, description="New task title (optional)", min_length=1, max_length=500)
    new_description: Optional[str] = Field(None, description="New task description (optional)", max_length=2000)

    @field_validator('new_title', 'new_description')
    @classmethod
    def check_at_least_one_field(cls, v, info):
        """Ensure at least one field is being updated."""
        # This validator runs for each field, so we need to check if both are None
        # We'll do a model-level validation instead
        return v

    def model_post_init(self, __context):
        """Validate that at least one field is provided after model initialization."""
        if self.new_title is None and self.new_description is None:
            raise ValueError("At least one of new_title or new_description must be provided")

    class Config:
        json_schema_extra = {
            "examples": [
                {"user_id": "user123", "task_id": 1, "new_title": "Buy organic milk", "new_description": None},
                {"user_id": "user123", "task_id": 2, "new_title": None, "new_description": "Updated description"},
                {"user_id": "user123", "task_id": 3, "new_title": "New title", "new_description": "New description"}
            ]
        }


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""
    user_id: str = Field(..., description="Authenticated user ID (required)", min_length=1)
    task_id: int = Field(..., description="Task ID to delete (required)", gt=0)

    class Config:
        json_schema_extra = {
            "examples": [
                {"user_id": "user123", "task_id": 1}
            ]
        }
