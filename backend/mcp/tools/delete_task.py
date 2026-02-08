"""Delete task tool for MCP server.

Permanently deletes tasks with ownership verification.
Tasks are removed from the database and cannot be recovered.
"""

import logging
from sqlmodel import Session, select

from ..schemas.base import ToolResponse, ErrorCodes
from ..schemas.task_inputs import DeleteTaskInput

# Import from backend modules
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from models.task import Task
from core.database import engine

logger = logging.getLogger(__name__)


def delete_task(input_data: DeleteTaskInput) -> ToolResponse:
    """
    Permanently delete a task.

    This tool removes a task from the database with strict ownership verification.
    Only the task owner can delete the task. Deletion is permanent and cannot be undone.

    Args:
        input_data: DeleteTaskInput with user_id and task_id

    Returns:
        ToolResponse with:
            - success=True, data={"task_id": N, "deleted": true} on success
            - success=False, error and error_code on failure

    Security:
        - ALWAYS verifies task ownership (user_id filter)
        - Returns TASK_NOT_FOUND if task doesn't exist or user doesn't own it
        - This prevents information leakage about task existence
    """
    try:
        # Validate user_id
        if not input_data.user_id or len(input_data.user_id.strip()) == 0:
            return ToolResponse(
                success=False,
                error="User ID is required and cannot be empty",
                error_code=ErrorCodes.INVALID_USER_ID
            )

        # Delete task from database with ownership verification
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

            # Store task_id before deletion
            task_id = task.id

            # Delete task
            session.delete(task)
            session.commit()

            # Return success response with task_id and deleted flag
            return ToolResponse(
                success=True,
                data={
                    "task_id": task_id,
                    "deleted": True
                }
            )

    except Exception as e:
        # Log full error for debugging
        logger.error(f"Database error in delete_task: {str(e)}", exc_info=True)

        # Return generic error to user (don't expose internal details)
        return ToolResponse(
            success=False,
            error="Failed to delete task due to a database error",
            error_code=ErrorCodes.DATABASE_ERROR
        )
