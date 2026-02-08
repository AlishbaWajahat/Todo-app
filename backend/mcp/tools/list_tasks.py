"""List tasks tool for MCP server.

Retrieves all tasks for a user with optional filtering by completion status and priority.
Enforces strict user isolation - users can only see their own tasks.
"""

import logging
from sqlmodel import Session, select
from typing import List, Dict, Any

from ..schemas.base import ToolResponse, ErrorCodes
from ..schemas.task_inputs import ListTasksInput

# Import from backend modules (relative to backend/)
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from models.task import Task
from core.database import engine

logger = logging.getLogger(__name__)


def list_tasks(input_data: ListTasksInput) -> ToolResponse:
    """
    List all tasks for a user with optional filtering.

    This tool retrieves tasks from the database with strict user isolation.
    Only tasks belonging to the specified user_id are returned.

    Args:
        input_data: ListTasksInput with user_id and optional filters

    Returns:
        ToolResponse with:
            - success=True, data={"tasks": [...], "count": N} on success
            - success=False, error and error_code on failure

    Security:
        - ALWAYS filters by user_id (no cross-user access)
        - Returns empty list if user has no tasks (not an error)
    """
    try:
        # Validate user_id
        if not input_data.user_id or len(input_data.user_id.strip()) == 0:
            return ToolResponse(
                success=False,
                error="User ID is required and cannot be empty",
                error_code=ErrorCodes.INVALID_USER_ID
            )

        # Query database with user isolation
        with Session(engine) as session:
            # Start with base query filtering by user_id (CRITICAL for security)
            statement = select(Task).where(Task.user_id == input_data.user_id)

            # Apply optional completed filter
            if input_data.completed is not None:
                statement = statement.where(Task.completed == input_data.completed)

            # Apply optional priority filter
            if input_data.priority is not None:
                statement = statement.where(Task.priority == input_data.priority)

            # Execute query
            tasks = session.exec(statement).all()

            # Convert tasks to dictionaries for JSON serialization
            tasks_data = []
            for task in tasks:
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
                tasks_data.append(task_dict)

            # Return success response with tasks and count
            return ToolResponse(
                success=True,
                data={
                    "tasks": tasks_data,
                    "count": len(tasks_data)
                }
            )

    except Exception as e:
        # Log full error for debugging
        logger.error(f"Database error in list_tasks: {str(e)}", exc_info=True)

        # Return generic error to user (don't expose internal details)
        return ToolResponse(
            success=False,
            error="Failed to retrieve tasks due to a database error",
            error_code=ErrorCodes.DATABASE_ERROR
        )
