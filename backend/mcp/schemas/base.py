"""Base schemas for MCP tool responses.

This module defines the standard response format used by all MCP tools
to ensure consistent error handling and data structure.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolResponse(BaseModel):
    """
    Standard response format for all MCP tools.

    Ensures consistent error handling and data structure across all tools.
    All tools MUST return this schema.

    Attributes:
        success: Whether the operation succeeded
        data: Response data (present on success)
        error: Human-readable error message (present on failure)
        error_code: Machine-readable error code (present on failure)
    """
    success: bool = Field(..., description="Whether the operation succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data (present on success)")
    error: Optional[str] = Field(None, description="Human-readable error message (present on failure)")
    error_code: Optional[str] = Field(None, description="Machine-readable error code (present on failure)")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "success": True,
                    "data": {"task": {"id": 1, "title": "Buy milk", "completed": False}},
                    "error": None,
                    "error_code": None
                },
                {
                    "success": False,
                    "data": None,
                    "error": "Task not found or you don't have permission to access it",
                    "error_code": "TASK_NOT_FOUND"
                }
            ]
        }


# Error code constants for consistent error handling
class ErrorCodes:
    """Standard error codes used across all MCP tools."""
    INVALID_USER_ID = "INVALID_USER_ID"  # user_id is missing, empty, or invalid format
    TASK_NOT_FOUND = "TASK_NOT_FOUND"    # Task doesn't exist or user doesn't own it
    VALIDATION_ERROR = "VALIDATION_ERROR"  # Input validation failed
    DATABASE_ERROR = "DATABASE_ERROR"    # Database connection or query failed
    INTERNAL_ERROR = "INTERNAL_ERROR"    # Unexpected error occurred
