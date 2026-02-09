"""
Response Formatter - Natural Language Response Generation

This module formats MCP tool outputs into concise, user-friendly natural language
responses. It translates structured data and error codes into conversational text.
"""
from typing import Dict, Any, Optional
from agent.intent_parser import IntentClassification, Intent


def format_response(intent: IntentClassification, tool_result: Dict[str, Any]) -> str:
    """
    Format tool result into natural language response.

    Args:
        intent: Classified intent with operation type
        tool_result: Result from MCP tool invocation

    Returns:
        Natural language response string (max 500 chars)

    Examples:
        >>> format_response(intent_create, {"success": True, "data": {"task": {"title": "Buy milk"}}})
        "Task created: Buy milk"

        >>> format_response(intent_list, {"success": True, "data": {"tasks": [...], "count": 3}})
        "You have 3 tasks: 1) Buy milk 2) Call dentist 3) Finish report"
    """
    # Handle UNKNOWN intent first (no tool was called)
    if intent.operation_type == Intent.UNKNOWN:
        return "I can only help with task management. Try 'create a task' or 'show my tasks'."

    # Check if tool invocation was successful
    if not tool_result.get("success", False):
        return format_error_response(
            tool_result.get("error_code", "INTERNAL_ERROR"),
            tool_result.get("error", "An error occurred")
        )

    # Format based on intent type
    if intent.operation_type == Intent.CREATE:
        return format_create_response(tool_result.get("data", {}))
    elif intent.operation_type == Intent.LIST:
        return format_list_response(tool_result.get("data", {}))
    elif intent.operation_type == Intent.COMPLETE:
        return format_complete_response(tool_result.get("data", {}))
    elif intent.operation_type == Intent.UPDATE:
        return format_update_response(tool_result.get("data", {}))
    elif intent.operation_type == Intent.DELETE:
        return format_delete_response(tool_result.get("data", {}))
    else:
        return "Something went wrong. Please try again."


def format_create_response(data: Dict[str, Any]) -> str:
    """
    Format CREATE operation response.

    Args:
        data: Tool result data containing created task

    Returns:
        Natural language confirmation message

    Examples:
        Simple: "Task created: Buy groceries"
        Detailed: "Task created: Buy groceries (priority: high, due: 2026-02-15)"
    """
    task = data.get("task", {})
    title = task.get("title", "Unknown task")

    # Check if we have additional details
    priority = task.get("priority")
    due_date = task.get("due_date")

    if priority or due_date:
        details = []
        if priority:
            details.append(f"priority: {priority}")
        if due_date:
            details.append(f"due: {due_date}")
        return f"Task created: {title} ({', '.join(details)})"
    else:
        return f"Task created: {title}"


def format_list_response(data: Dict[str, Any]) -> str:
    """
    Format LIST operation response.

    Args:
        data: Tool result data containing tasks array and count

    Returns:
        Natural language list of tasks

    Examples:
        With tasks: "You have 3 tasks: 1) Buy milk 2) Call dentist 3) Finish report"
        No tasks: "You have no tasks"
        Many tasks: "You have 15 tasks: 1) Task1 2) Task2 ... (showing first 10)"
    """
    tasks = data.get("tasks", []) or []  # Handle None case
    count = data.get("count", len(tasks))

    if count == 0:
        return "You have no tasks"

    # Format task list (max 10 tasks to keep response concise)
    task_list = []
    for i, task in enumerate(tasks[:10], 1):
        title = task.get("title", "Untitled")
        completed = task.get("completed", False)
        status = "✓" if completed else ""
        task_list.append(f"{i}) {status}{title}".strip())

    tasks_text = " ".join(task_list)

    if count > 10:
        return f"You have {count} tasks: {tasks_text} (showing first 10)"
    else:
        return f"You have {count} task{'s' if count != 1 else ''}: {tasks_text}"


def format_complete_response(data: Dict[str, Any]) -> str:
    """
    Format COMPLETE operation response.

    Args:
        data: Tool result data containing updated task

    Returns:
        Natural language confirmation message

    Examples:
        Completed: "Marked 'Buy milk' as done"
        Uncompleted: "Marked 'Buy milk' as not done"
    """
    task = data.get("task", {})
    title = task.get("title", "task")
    completed = task.get("completed", True)

    if completed:
        return f"Marked '{title}' as done"
    else:
        return f"Marked '{title}' as not done"


def format_update_response(data: Dict[str, Any]) -> str:
    """
    Format UPDATE operation response.

    Args:
        data: Tool result data containing updated task

    Returns:
        Natural language confirmation message

    Examples:
        Title change: "Updated 'Buy milk' to 'Buy organic milk'"
        Description change: "Updated task 3 description"
    """
    task = data.get("task", {})
    old_title = data.get("old_title")
    new_title = task.get("title")

    if old_title and new_title and old_title != new_title:
        return f"Updated '{old_title}' to '{new_title}'"
    elif new_title:
        return f"Updated task '{new_title}'"
    else:
        task_id = task.get("id", "")
        return f"Updated task {task_id}"


def format_delete_response(data: Dict[str, Any]) -> str:
    """
    Format DELETE operation response.

    Args:
        data: Tool result data containing deleted task info

    Returns:
        Natural language confirmation message

    Examples:
        "Deleted task 'Buy milk'"
    """
    task = data.get("task", {})
    title = task.get("title", "task")
    return f"Deleted task '{title}'"


def format_error_response(error_code: str, error_message: str) -> str:
    """
    Format error response into user-friendly message.

    Translates technical error codes into natural language guidance.

    Args:
        error_code: Machine-readable error code
        error_message: Technical error message

    Returns:
        User-friendly error message

    Error Code Mappings:
        TASK_NOT_FOUND -> "I couldn't find that task. Try listing your tasks first."
        VALIDATION_ERROR -> "Invalid input: {details}"
        DATABASE_ERROR -> "Something went wrong. Please try again."
        INTERNAL_ERROR -> "An error occurred. Please try again."
    """
    error_map = {
        "TASK_NOT_FOUND": "I couldn't find that task. Try listing your tasks first.",
        "VALIDATION_ERROR": f"Invalid input: {error_message}",
        "DATABASE_ERROR": "Something went wrong. Please try again.",
        "INTERNAL_ERROR": "An error occurred. Please try again.",
        "INVALID_USER_ID": "User authentication failed. Please log in again.",
    }

    return error_map.get(error_code, "Something went wrong. Please try again.")
