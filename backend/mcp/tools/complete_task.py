"""Complete task tool for MCP server.

Marks tasks as complete or incomplete with ownership verification.
Updates the task's completed status and updated_at timestamp.
"""

import logging
from sqlmodel import Session, select
from datetime import datetime

from ..schemas.base import ToolResponse, ErrorCodes
from ..schemas.task_inputs import CompleteTaskInput

# Import from backend modules
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from models.task import Task
from core.database import engine

logger = logging.getLogger(__name__)


def complete_task(input_data: CompleteTaskInput) -> ToolResponse:
    """
    Mark a task as complete or incomplete.

    This tool updates the completion status of a task with strict ownership verification.
    Only the task owner can update the completion status.

    Args:
        input_data: CompleteTaskInput with user_id, task_id, and completed status

    Returns:
        ToolResponse with:
            - success=True, data={"task": {...}} on success
            - success=False, error and error_code on failure

    Security:
        - ALWAYS verifies task ownership (user_id filter)
        - Returns TASK_NOT_FOUND if task doesn't exist or user doesn't own it
        - This prevents information leakage about task existence
    """
    print(f"MCP complete_task received for user ID: {input_data.user_id}, task_id: {input_data.task_id}, completed: {input_data.completed}")
    try:
        # Validate user_id
        if not input_data.user_id or len(input_data.user_id.strip()) == 0:
            return ToolResponse(
                success=False,
                error="User ID is required and cannot be empty",
                error_code=ErrorCodes.INVALID_USER_ID
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

            # Update completion status and timestamp
            task.completed = input_data.completed
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
        logger.error(f"Database error in complete_task: {str(e)}", exc_info=True)

        # Return generic error to user (don't expose internal details)
        return ToolResponse(
            success=False,
            error="Failed to update task due to a database error",
            error_code=ErrorCodes.DATABASE_ERROR
        )
