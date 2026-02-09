"""
Stateless Task Agent - Main Agent Module

This module provides the core agent functionality for processing natural language
task management requests using OpenAI Agent SDK with Gemini routing.
"""
import os
import time
from typing import Dict, Any, Optional
from agents import Agent, Runner, set_tracing_disabled, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
from pydantic import BaseModel

from core.config import settings
from agent.intent_parser import parse_intent, IntentClassification, Intent
from agent.response_formatter import format_response

# Import MCP tools
from mcp.tools.list_tasks import list_tasks
from mcp.tools.add_task import add_task
from mcp.tools.complete_task import complete_task
from mcp.tools.update_task import update_task
from mcp.tools.delete_task import delete_task

# Import MCP tool input schemas
from mcp.schemas.task_inputs import (
    ListTasksInput,
    AddTaskInput,
    CompleteTaskInput,
    UpdateTaskInput,
    DeleteTaskInput
)


# Disable tracing for cleaner output
set_tracing_disabled(disabled=True)


class AgentRequest(BaseModel):
    """Request schema for agent endpoint."""
    user_id: str
    message: str


class AgentResponse(BaseModel):
    """Response schema for agent endpoint."""
    response: str
    metadata: Optional[Dict[str, Any]] = None


# Initialize AsyncOpenAI client with Gemini routing
external_client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url=settings.openai_base_url,
)

# Create OpenAI Chat Completions Model with Gemini
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

# Create RunConfig with model and tracing disabled
config = RunConfig(
    model=model,
    tracing_disabled=True
)


async def process_request(user_id: str, message: str) -> AgentResponse:
    """
    Process a natural language task management request.

    This is the main entry point for the stateless agent. It:
    1. Parses the user message to identify intent and extract parameters
    2. Invokes the appropriate MCP tool based on the intent
    3. Formats the tool response into natural language

    Args:
        user_id: Pre-authenticated user identifier
        message: Natural language message from user

    Returns:
        AgentResponse with natural language response and metadata

    Note:
        This function is stateless - it maintains no state between requests.
    """
    start_time = time.time()

    try:
        # Step 1: Parse intent and extract parameters
        intent_classification = parse_intent(message)

        # Step 2: Invoke appropriate MCP tool based on intent
        tool_result = await invoke_tool(user_id, intent_classification)

        # Step 3: Format response
        response_text = format_response(intent_classification, tool_result)

        # Calculate execution time (minimum 1ms to avoid 0 for very fast operations)
        execution_time_ms = max(1, int((time.time() - start_time) * 1000))

        # Return response with metadata
        return AgentResponse(
            response=response_text,
            metadata={
                "intent": intent_classification.operation_type,
                "tool_called": tool_result.get("tool_name"),
                "confidence": intent_classification.confidence,
                "execution_time_ms": execution_time_ms
            }
        )

    except Exception as e:
        # Handle all exceptions and return user-friendly error
        execution_time_ms = int((time.time() - start_time) * 1000)
        return AgentResponse(
            response="Something went wrong. Please try again.",
            metadata={
                "intent": "ERROR",
                "tool_called": None,
                "confidence": 0.0,
                "execution_time_ms": execution_time_ms,
                "error": str(e)
            }
        )


async def invoke_tool(user_id: str, intent: IntentClassification) -> Dict[str, Any]:
    """
    Invoke the appropriate MCP tool based on the classified intent.

    Args:
        user_id: User identifier for tool invocation
        intent: Classified intent with extracted parameters

    Returns:
        Dictionary with tool_name, success, data, error, and error_code

    Note:
        All MCP tools are called synchronously. The async wrapper is for
        future compatibility with async tool implementations.
    """
    try:
        if intent.operation_type == Intent.CREATE:
            return invoke_add_task(user_id, intent.extracted_parameters)
        elif intent.operation_type == Intent.LIST:
            return invoke_list_tasks(user_id, intent.extracted_parameters)
        elif intent.operation_type == Intent.COMPLETE:
            return invoke_complete_task(user_id, intent.extracted_parameters)
        elif intent.operation_type == Intent.UPDATE:
            return invoke_update_task(user_id, intent.extracted_parameters)
        elif intent.operation_type == Intent.DELETE:
            return invoke_delete_task(user_id, intent.extracted_parameters)
        elif intent.operation_type == Intent.UNKNOWN:
            return {
                "tool_name": None,
                "success": False,
                "data": None,
                "error": "Unknown intent",
                "error_code": "UNKNOWN_INTENT"
            }
        else:
            return {
                "tool_name": None,
                "success": False,
                "data": None,
                "error": "Unsupported operation",
                "error_code": "INTERNAL_ERROR"
            }
    except Exception as e:
        return {
            "tool_name": None,
            "success": False,
            "data": None,
            "error": str(e),
            "error_code": "INTERNAL_ERROR"
        }


def invoke_add_task(user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke add_task MCP tool to create a new task.

    Args:
        user_id: User identifier
        params: Extracted parameters (title, description, priority, due_date)

    Returns:
        Dictionary with tool result
    """
    try:
        # Create input for add_task tool
        tool_input = AddTaskInput(
            user_id=user_id,
            title=params.get("title", "Untitled task"),
            description=params.get("description"),
            priority=params.get("priority"),
            due_date=params.get("due_date")
        )

        # Call MCP tool
        tool_response = add_task(tool_input)

        # Convert ToolResponse to dictionary
        return {
            "tool_name": "add_task",
            "success": tool_response.success,
            "data": tool_response.data,
            "error": tool_response.error,
            "error_code": tool_response.error_code
        }
    except Exception as e:
        return {
            "tool_name": "add_task",
            "success": False,
            "data": None,
            "error": str(e),
            "error_code": "INTERNAL_ERROR"
        }


def invoke_list_tasks(user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke list_tasks MCP tool to retrieve user's tasks.

    Args:
        user_id: User identifier
        params: Extracted parameters (completed, priority filters)

    Returns:
        Dictionary with tool result
    """
    try:
        # Create input for list_tasks tool
        tool_input = ListTasksInput(
            user_id=user_id,
            completed=params.get("completed"),
            priority=params.get("priority")
        )

        # Call MCP tool
        tool_response = list_tasks(tool_input)

        # Convert ToolResponse to dictionary
        return {
            "tool_name": "list_tasks",
            "success": tool_response.success,
            "data": tool_response.data,
            "error": tool_response.error,
            "error_code": tool_response.error_code
        }
    except Exception as e:
        return {
            "tool_name": "list_tasks",
            "success": False,
            "data": None,
            "error": str(e),
            "error_code": "INTERNAL_ERROR"
        }


def invoke_complete_task(user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke complete_task MCP tool to toggle task completion status.

    Args:
        user_id: User identifier
        params: Extracted parameters (task_id, task_title, completed)

    Returns:
        Dictionary with tool result
    """
    try:
        # Identify task by ID or title
        task_id = identify_task(user_id, params.get("task_id"), params.get("task_title"))

        if task_id is None:
            return {
                "tool_name": "complete_task",
                "success": False,
                "data": None,
                "error": "Task not found",
                "error_code": "TASK_NOT_FOUND"
            }

        # Create input for complete_task tool
        tool_input = CompleteTaskInput(
            user_id=user_id,
            task_id=task_id,
            completed=params.get("completed", True)
        )

        # Call MCP tool
        tool_response = complete_task(tool_input)

        # Convert ToolResponse to dictionary
        return {
            "tool_name": "complete_task",
            "success": tool_response.success,
            "data": tool_response.data,
            "error": tool_response.error,
            "error_code": tool_response.error_code
        }
    except Exception as e:
        return {
            "tool_name": "complete_task",
            "success": False,
            "data": None,
            "error": str(e),
            "error_code": "INTERNAL_ERROR"
        }


def identify_task(user_id: str, task_id: Optional[int], task_title: Optional[str]) -> Optional[int]:
    """
    Identify a task by ID or title using fuzzy matching.

    Args:
        user_id: User identifier
        task_id: Task ID if provided (validated against user's tasks)
        task_title: Task title if provided (fuzzy match with 70% similarity)

    Returns:
        Task ID if found, None otherwise

    Note:
        Always queries user's tasks to validate task_id or find by title.
        Uses simple substring matching (70% threshold) for fuzzy matching.
    """
    try:
        # Get all user's tasks
        tool_input = ListTasksInput(user_id=user_id, completed=None, priority=None)
        tool_response = list_tasks(tool_input)

        if not tool_response.success or not tool_response.data:
            return None

        tasks = tool_response.data.get("tasks", [])

        # If task_id provided, validate it exists in user's tasks
        if task_id is not None:
            for task in tasks:
                if task.get("id") == task_id:
                    return task_id
            # Task ID not found in user's tasks
            return None

        # If task_title provided, find by fuzzy match
        if task_title:
            # Find best match using simple substring matching
            best_match = None
            best_score = 0.0

            task_title_lower = task_title.lower()

            for task in tasks:
                title = task.get("title", "").lower()

                # Calculate similarity score (simple approach)
                # Check if task_title is substring of title or vice versa
                if task_title_lower in title:
                    score = len(task_title_lower) / len(title)
                elif title in task_title_lower:
                    score = len(title) / len(task_title_lower)
                else:
                    # Calculate character overlap
                    common_chars = sum(1 for c in task_title_lower if c in title)
                    score = common_chars / max(len(task_title_lower), len(title))

                # Keep track of best match
                if score > best_score and score >= 0.7:  # 70% threshold
                    best_score = score
                    best_match = task.get("id")

            return best_match

    except Exception:
        return None

    # No task_id or task_title provided
    return None


def invoke_update_task(user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke update_task MCP tool to update task details.

    Args:
        user_id: User identifier
        params: Extracted parameters (task_id, task_title, new_title, new_description)

    Returns:
        Dictionary with tool result
    """
    try:
        # Identify task by ID or title
        task_id = identify_task(user_id, params.get("task_id"), params.get("task_title"))

        if task_id is None:
            return {
                "tool_name": "update_task",
                "success": False,
                "data": None,
                "error": "Task not found",
                "error_code": "TASK_NOT_FOUND"
            }

        # Validate at least one field is provided
        new_title = params.get("new_title")
        new_description = params.get("new_description")

        if not new_title and not new_description:
            return {
                "tool_name": "update_task",
                "success": False,
                "data": None,
                "error": "At least one of new_title or new_description must be provided",
                "error_code": "VALIDATION_ERROR"
            }

        # Store old title for response formatting
        old_title = params.get("task_title")

        # Create input for update_task tool
        tool_input = UpdateTaskInput(
            user_id=user_id,
            task_id=task_id,
            new_title=new_title,
            new_description=new_description
        )

        # Call MCP tool
        tool_response = update_task(tool_input)

        # Add old_title to response data for formatting
        if tool_response.success and tool_response.data:
            tool_response.data["old_title"] = old_title

        # Convert ToolResponse to dictionary
        return {
            "tool_name": "update_task",
            "success": tool_response.success,
            "data": tool_response.data,
            "error": tool_response.error,
            "error_code": tool_response.error_code
        }
    except Exception as e:
        return {
            "tool_name": "update_task",
            "success": False,
            "data": None,
            "error": str(e),
            "error_code": "INTERNAL_ERROR"
        }


def invoke_delete_task(user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke delete_task MCP tool to delete a task.

    Args:
        user_id: User identifier
        params: Extracted parameters (task_id, task_title)

    Returns:
        Dictionary with tool result
    """
    try:
        # Identify task by ID or title
        task_id = identify_task(user_id, params.get("task_id"), params.get("task_title"))

        if task_id is None:
            return {
                "tool_name": "delete_task",
                "success": False,
                "data": None,
                "error": "Task not found",
                "error_code": "TASK_NOT_FOUND"
            }

        # Create input for delete_task tool
        tool_input = DeleteTaskInput(
            user_id=user_id,
            task_id=task_id
        )

        # Call MCP tool
        tool_response = delete_task(tool_input)

        # Convert ToolResponse to dictionary
        return {
            "tool_name": "delete_task",
            "success": tool_response.success,
            "data": tool_response.data,
            "error": tool_response.error,
            "error_code": tool_response.error_code
        }
    except Exception as e:
        return {
            "tool_name": "delete_task",
            "success": False,
            "data": None,
            "error": str(e),
            "error_code": "INTERNAL_ERROR"
        }
