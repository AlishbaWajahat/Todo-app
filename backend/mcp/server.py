"""MCP Server initialization for task management tools.

This module initializes the MCP server and registers all task management tools.
The server communicates via stdio and provides 5 tools for AI agents to manage tasks.
"""

import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("task-tools-server")

logger.info("MCP Server initialized: task-tools-server")


# Import tool implementations
from .tools.list_tasks import list_tasks as list_tasks_impl
from .tools.add_task import add_task as add_task_impl
from .tools.complete_task import complete_task as complete_task_impl
from .tools.update_task import update_task as update_task_impl
from .tools.delete_task import delete_task as delete_task_impl
from .schemas.task_inputs import (
    ListTasksInput,
    AddTaskInput,
    CompleteTaskInput,
    UpdateTaskInput,
    DeleteTaskInput
)


# Tool registration
@server.tool()
async def list_tasks(user_id: str, completed: bool = None, priority: str = None) -> dict:
    """
    List all tasks for a user with optional filtering.

    Retrieves tasks from the database with strict user isolation.
    Only tasks belonging to the specified user_id are returned.

    Args:
        user_id: Authenticated user ID (required)
        completed: Filter by completion status (optional)
        priority: Filter by priority: low, medium, high (optional)

    Returns:
        Dictionary with success, data (tasks array and count), error, and error_code
    """
    # Create input schema
    input_data = ListTasksInput(
        user_id=user_id,
        completed=completed,
        priority=priority
    )

    # Call implementation (sync function)
    result = list_tasks_impl(input_data)

    # Return as dictionary
    return result.model_dump()


logger.info("Registered tool: list_tasks")


@server.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = None,
    priority: str = None,
    due_date: str = None
) -> dict:
    """
    Create a new task for a user.

    Creates a task in the database with the specified attributes.
    The task is created with completed=false by default.

    Args:
        user_id: Authenticated user ID (required)
        title: Task title (required, 1-500 characters)
        description: Task description (optional, max 2000 characters)
        priority: Task priority: low, medium, high (optional)
        due_date: Task due date in ISO 8601 format (optional)

    Returns:
        Dictionary with success, data (created task), error, and error_code
    """
    from datetime import datetime

    # Parse due_date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            pass  # Let validation handle it

    # Create input schema
    input_data = AddTaskInput(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
        due_date=parsed_due_date
    )

    # Call implementation (sync function)
    result = add_task_impl(input_data)

    # Return as dictionary
    return result.model_dump()


logger.info("Registered tool: add_task")


@server.tool()
async def complete_task(user_id: str, task_id: int, completed: bool) -> dict:
    """
    Mark a task as complete or incomplete.

    Updates the completion status of a task with strict ownership verification.
    Only the task owner can update the completion status.

    Args:
        user_id: Authenticated user ID (required)
        task_id: Task ID to update (required, positive integer)
        completed: New completion status (required, true or false)

    Returns:
        Dictionary with success, data (updated task), error, and error_code
    """
    # Create input schema
    input_data = CompleteTaskInput(
        user_id=user_id,
        task_id=task_id,
        completed=completed
    )

    # Call implementation (sync function)
    result = complete_task_impl(input_data)

    # Return as dictionary
    return result.model_dump()


logger.info("Registered tool: complete_task")


@server.tool()
async def update_task(
    user_id: str,
    task_id: int,
    new_title: str = None,
    new_description: str = None
) -> dict:
    """
    Update task title and/or description.

    Updates task details with strict ownership verification.
    Supports partial updates - can update title only, description only, or both.

    Args:
        user_id: Authenticated user ID (required)
        task_id: Task ID to update (required, positive integer)
        new_title: New task title (optional, 1-500 characters)
        new_description: New task description (optional, max 2000 characters)

    Returns:
        Dictionary with success, data (updated task), error, and error_code
    """
    # Create input schema
    input_data = UpdateTaskInput(
        user_id=user_id,
        task_id=task_id,
        new_title=new_title,
        new_description=new_description
    )

    # Call implementation (sync function)
    result = update_task_impl(input_data)

    # Return as dictionary
    return result.model_dump()


logger.info("Registered tool: update_task")


@server.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """
    Permanently delete a task.

    Removes a task from the database with strict ownership verification.
    Only the task owner can delete the task. Deletion is permanent and cannot be undone.

    Args:
        user_id: Authenticated user ID (required)
        task_id: Task ID to delete (required, positive integer)

    Returns:
        Dictionary with success, data (task_id and deleted flag), error, and error_code
    """
    # Create input schema
    input_data = DeleteTaskInput(
        user_id=user_id,
        task_id=task_id
    )

    # Call implementation (sync function)
    result = delete_task_impl(input_data)

    # Return as dictionary
    return result.model_dump()


logger.info("Registered tool: delete_task")


async def main():
    """Run the MCP server via stdio."""
    logger.info("Starting MCP server on stdio...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
