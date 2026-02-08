"""Update task tool for MCP server.

Updates task title and/or description with ownership verification.
Supports partial updates (title only, description only, or both).
"""

import logging
from sqlmodel import Session, select
from datetime import datetime

from ..schemas.base import ToolResponse, ErrorCodes
from ..schemas.task_inputs import UpdateTaskInput

# Import from backend modules
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from models.task import Task
from core.database import engine

logger = logging.getLogger(__name__)


def update_task(input_data: UpdateTaskInput) -> ToolResponse:
    """
    Update task title and/or description.

    This tool updates task details with strict ownership verification.
    Supports partial updates - can update title only, description only, or both.

    Args:
        input_data: UpdateTaskInput with user_id, task_id, and optional new_title/new_description

    Returns:
        ToolResponse with:
            - success=True, data={"task": {...}} on success
            - success=False, error and error_code on failure

    Validation:
        - At least one of new_title or new_description must be provided
        - new_title: 1-500 characters (if provided)
        - new_description: max 2000 characters (if provided)

    Security:
        - ALWAYS verifies task ownership (user_id filter)
        - Returns TASK_NOT_FOUND if task doesn't exist or user doesn't own it
    """
    try:
        # Validate user_id
        if not input_data.user_id or len(input_data.user_id.strip()) == 0:
            return ToolResponse(
                success=False,
                error="User ID is required and cannot be empty",
                error_code=ErrorCodes.INVALID_USER_ID
            )

        # Validate that at least one field is being updated
        if input_data.new_title is None and input_data.new_description is None:
            return ToolResponse(
                success=False,
                error="At least one of new_title or new_description must be provided",
                error_code=ErrorCodes.VALIDATION_ERROR
            )

        # Validate new_title length if provided
        if input_data.new_title and len(input_data.new_title) > 500:
            return ToolResponse(
                success=False,
                error="Task title must be 500 characters or less",
                error_code=ErrorCodes.VALIDATION_ERROR
            )

        # Validate new_description length if provided
        if input_data.new_description and len(input_data.new_description) > 2000:
            return ToolResponse(
                success=False,
                error="Task description must be 2000 characters or less",
                error_code=ErrorCodes.VALIDATION_ERROR
            )

        # Update task in database with ownership verification
        with Session(engine) as session:
            # Query task with user_id filter (CRITICAL for security)
            statement = select(Task).where(
                Task.id == input_data.task_id,
                Task.user_id == input_data.user_id
            )
            task = session.exec(statement).first()

            # Check if task exists and user owns it
            if not task:
                return ToolResponse(
                    success=False,
                    error="Task not found or you don't have permission to access it",
                    error_code=ErrorCodes.TASK_NOT_FOUND
                )

            # Update fields (partial update support)
            if input_data.new_title is not None:
                task.title = input_data.new_title

            if input_data.new_description is not None:
                task.description = input_data.new_description

            # Always update timestamp
            task.updated_at = datetime.utcnow()

            # Commit changes
            session.add(task)
            session.commit()
            session.refresh(task)

            # Convert task to dictionary for JSON serialization
            task_dict = {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            }

            # Return success response with updated task
            return ToolResponse(
                success=True,
                data={"task": task_dict}
            )

    except Exception as e:
        # Log full error for debugging
        logger.error(f"Database error in update_task: {str(e)}", exc_info=True)

        # Return generic error to user (don't expose internal details)
        return ToolResponse(
            success=False,
            error="Failed to update task due to a database error",
            error_code=ErrorCodes.DATABASE_ERROR
        )
