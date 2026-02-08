"""Add task tool for MCP server.

Creates new tasks for users with input validation and user_id enforcement.
All tasks are created with completed=false by default.
"""

import logging
from sqlmodel import Session
from datetime import datetime

from ..schemas.base import ToolResponse, ErrorCodes
from ..schemas.task_inputs import AddTaskInput

# Import from backend modules
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from models.task import Task
from core.database import engine

logger = logging.getLogger(__name__)


def add_task(input_data: AddTaskInput) -> ToolResponse:
    """
    Create a new task for a user.

    This tool creates a task in the database with the specified attributes.
    The task is created with completed=false by default.

    Args:
        input_data: AddTaskInput with user_id, title, and optional fields

    Returns:
        ToolResponse with:
            - success=True, data={"task": {...}} on success
            - success=False, error and error_code on failure

    Validation:
        - user_id: Required, non-empty string
        - title: Required, 1-500 characters
        - description: Optional, max 2000 characters
        - priority: Optional string
        - due_date: Optional datetime

    Security:
        - Task is created with the provided user_id (ownership enforced)
    """
    try:
        # Validate user_id
        if not input_data.user_id or len(input_data.user_id.strip()) == 0:
            return ToolResponse(
                success=False,
                error="User ID is required and cannot be empty",
                error_code=ErrorCodes.INVALID_USER_ID
            )

        # Validate title length (Pydantic already validates, but double-check)
        if len(input_data.title) > 500:
            return ToolResponse(
                success=False,
                error="Task title must be 500 characters or less",
                error_code=ErrorCodes.VALIDATION_ERROR
            )

        # Validate description length if provided
        if input_data.description and len(input_data.description) > 2000:
            return ToolResponse(
                success=False,
                error="Task description must be 2000 characters or less",
                error_code=ErrorCodes.VALIDATION_ERROR
            )

        # Create task in database
        with Session(engine) as session:
            # Create new task with provided data
            new_task = Task(
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                completed=False,  # Always start as incomplete
                priority=input_data.priority,
                due_date=input_data.due_date,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Add to session and commit
            session.add(new_task)
            session.commit()
            session.refresh(new_task)

            # Convert task to dictionary for JSON serialization
            task_dict = {
                "id": new_task.id,
                "user_id": new_task.user_id,
                "title": new_task.title,
                "description": new_task.description,
                "completed": new_task.completed,
                "priority": new_task.priority,
                "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                "created_at": new_task.created_at.isoformat() if new_task.created_at else None,
                "updated_at": new_task.updated_at.isoformat() if new_task.updated_at else None,
            }

            # Return success response with created task
            return ToolResponse(
                success=True,
                data={"task": task_dict}
            )

    except Exception as e:
        # Log full error for debugging
        logger.error(f"Database error in add_task: {str(e)}", exc_info=True)

        # Return generic error to user (don't expose internal details)
        return ToolResponse(
            success=False,
            error="Failed to create task due to a database error",
            error_code=ErrorCodes.DATABASE_ERROR
        )
