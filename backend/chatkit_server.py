"""
ChatKit Server Integration Utility

This module provides utility functions for integrating OpenAI ChatKit with the FastAPI backend.
It wraps the existing chat endpoint logic and provides format conversion helpers.

Note: The main chat endpoint (api/v1/endpoints/chat.py) already handles all the core functionality.
This module serves as a utility layer for ChatKit-specific operations.
"""
from typing import Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel


class ChatKitMessage(BaseModel):
    """ChatKit message format."""
    message: str
    metadata: Optional[Dict[str, Any]] = None


class ChatKitRequest(BaseModel):
    """
    ChatKit request format.

    This matches the format expected by OpenAI ChatKit's onSendMessage callback.
    """
    message: str
    conversation_id: Optional[str] = None


class ChatKitResponse(BaseModel):
    """
    ChatKit response format.

    This is the format expected by OpenAI ChatKit's onSendMessage callback return value.
    """
    message: str
    metadata: Optional[Dict[str, Any]] = None


def convert_to_chatkit_response(
    response: str,
    conversation_id: UUID,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convert backend chat response to ChatKit format.

    Args:
        response: Agent response text
        conversation_id: Conversation UUID
        metadata: Optional metadata from agent

    Returns:
        Dictionary in ChatKit response format

    Example:
        >>> convert_to_chatkit_response(
        ...     "Task created successfully",
        ...     UUID("550e8400-e29b-41d4-a716-446655440000"),
        ...     {"intent": "CREATE", "tool_called": "add_task"}
        ... )
        {
            "message": "Task created successfully",
            "metadata": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "intent": "CREATE",
                "tool_called": "add_task"
            }
        }
    """
    # Merge conversation_id into metadata
    chatkit_metadata = metadata.copy() if metadata else {}
    chatkit_metadata["conversation_id"] = str(conversation_id)

    return {
        "message": response,
        "metadata": chatkit_metadata
    }


def extract_conversation_id(chatkit_metadata: Optional[Dict[str, Any]]) -> Optional[UUID]:
    """
    Extract conversation_id from ChatKit metadata.

    Args:
        chatkit_metadata: Metadata from ChatKit request

    Returns:
        UUID if found and valid, None otherwise

    Example:
        >>> extract_conversation_id({"conversation_id": "550e8400-e29b-41d4-a716-446655440000"})
        UUID('550e8400-e29b-41d4-a716-446655440000')
    """
    if not chatkit_metadata:
        return None

    conversation_id_str = chatkit_metadata.get("conversation_id")
    if not conversation_id_str:
        return None

    try:
        return UUID(conversation_id_str)
    except (ValueError, AttributeError):
        return None


def format_error_response(error_message: str, error_code: str = "ERROR") -> Dict[str, Any]:
    """
    Format an error response for ChatKit.

    Args:
        error_message: Human-readable error message
        error_code: Error code for client-side handling

    Returns:
        Dictionary in ChatKit response format with error information

    Example:
        >>> format_error_response("Task not found", "TASK_NOT_FOUND")
        {
            "message": "Task not found",
            "metadata": {
                "error": True,
                "error_code": "TASK_NOT_FOUND"
            }
        }
    """
    return {
        "message": error_message,
        "metadata": {
            "error": True,
            "error_code": error_code
        }
    }


def validate_chatkit_message(message: str) -> tuple[bool, Optional[str]]:
    """
    Validate a ChatKit message.

    Args:
        message: Message text to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if message is valid, False otherwise
        - error_message: Error description if invalid, None if valid

    Example:
        >>> validate_chatkit_message("Add a task")
        (True, None)
        >>> validate_chatkit_message("")
        (False, "Message cannot be empty")
        >>> validate_chatkit_message("x" * 3000)
        (False, "Message exceeds maximum length of 2000 characters")
    """
    if not message or not message.strip():
        return False, "Message cannot be empty"

    if len(message) > 2000:
        return False, "Message exceeds maximum length of 2000 characters"

    return True, None


# ChatKit configuration constants
CHATKIT_CONFIG = {
    "max_message_length": 2000,
    "greeting": "Hello! I can help you manage your tasks. Try asking me to add, list, update, complete, or delete tasks.",
    "placeholder": "Ask me to manage your tasks...",
    "prompts": [
        {"label": "Add a task", "prompt": "Add a task to buy groceries"},
        {"label": "Show my tasks", "prompt": "Show me all my tasks"},
        {"label": "Complete a task", "prompt": "Mark task 1 as complete"},
        {"label": "Update a task", "prompt": "Update task 2 title to 'Buy organic milk'"},
        {"label": "Delete a task", "prompt": "Delete task 3"},
    ],
    "theme": {
        "primaryColor": "#3b82f6",
        "backgroundColor": "#ffffff",
        "textColor": "#1f2937",
    }
}
