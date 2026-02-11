"""
Stateless Task Agent - Main Agent Module

This module provides the core agent functionality for processing natural language
task management requests using OpenAI Agent SDK with Gemini routing.

The agent is designed to be a friendly, supportive daily companion that helps users
manage their tasks while also being there to listen when they need to talk.
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


def is_casual_conversation(message: str) -> bool:
    """
    Determine if the message is casual conversation vs a task operation request.

    Returns True for casual greetings, feelings, questions, or general chat.
    Returns False for clear task operations (add, delete, complete, update, list).

    IMPORTANT: Check for explicit task requests FIRST!
    """
    message_lower = message.lower().strip()

    # FIRST: Check for EXPLICIT task operation requests (must be very clear)
    explicit_task_keywords = [
        "add task", "create task", "new task", "make task",
        "delete task", "remove task",
        "update task", "change task", "modify task", "edit task",
        "list task", "show task", "view task", "my tasks", "get tasks",
        "mark task", "complete task",
    ]

    # If message has explicit task keyword, it's definitely a task operation
    for keyword in explicit_task_keywords:
        if keyword in message_lower:
            return False

    # Check for task completion patterns with "mark" or "done"
    if "mark" in message_lower and ("done" in message_lower or "complete" in message_lower):
        return False

    # SECOND: Check for casual conversation indicators
    # Greetings
    pure_greetings = ["hi", "hello", "hey", "yo", "sup", "wassup", "good morning", "good evening"]
    if any(g in message_lower for g in pure_greetings) and "task" not in message_lower:
        return True

    # Sharing personal updates (past tense actions)
    sharing_patterns = [
        "i went", "i bought", "i did", "i had", "i saw", "i met",
        "today i", "yesterday i", "last night i",
        "just", "recently",
    ]
    if any(pattern in message_lower for pattern in sharing_patterns) and "task" not in message_lower:
        # Make sure it's not a completion request
        if not any(word in message_lower for word in ["mark", "complete", "done", "finished"]):
            return True

    # Thanks
    if any(word in message_lower for word in ["thank", "thanks", "appreciate"]) and "task" not in message_lower:
        return True

    # Feelings/emotions
    feeling_patterns = [
        "how are you", "what's up",
        "i feel", "i'm feeling", "feeling",
        "my day", "today was", "had a", "been",
        "tired", "exhausted", "stressed", "frustrated",
        "happy", "excited", "sad",
    ]
    if any(pattern in message_lower for pattern in feeling_patterns) and "task" not in message_lower:
        return True

    # Questions about the agent
    if any(phrase in message_lower for phrase in ["who are you", "what are you", "what can you", "how do you"]) and "task" not in message_lower:
        return True

    # Goodbyes
    if any(word in message_lower for word in ["bye", "goodbye", "see you", "good night"]):
        return True

    # THIRD: If message is short and vague, treat as casual
    if len(message_lower.split()) <= 5 and "task" not in message_lower:
        # No explicit task keywords, probably casual
        return True

    # Default: If ambiguous, treat as task operation
    return False


async def generate_casual_response(message: str) -> str:
    """
    Generate a friendly, empathetic response for casual conversation.

    The agent is designed to be a supportive companion that listens and responds
    warmly to the user's feelings and experiences.
    """
    message_lower = message.lower().strip()

    # Greetings
    if any(word in message_lower for word in ["hi", "hello", "hey", "good morning", "good evening"]):
        return "Hey there! 💜 How can I help you today? Whether you need help with tasks or just want to chat, I'm here for you!"

    # Thanks
    if any(word in message_lower for word in ["thank", "thanks", "appreciate"]):
        return "You're so welcome! I'm always here to help and support you. Keep crushing those goals! 💪✨"

    # User sharing accomplishments or activities (bought, did, went, etc.)
    if any(pattern in message_lower for pattern in ["i bought", "i did", "i went", "i had", "i finished"]):
        return "Nice! 🌟 Sounds like you've been productive! Want to add that to your task list to track it, or just sharing your day with me? Either way, I'm here! 💜"

    # Positive feelings
    if any(word in message_lower for word in ["great", "awesome", "happy", "excited", "good day", "went well"]):
        return "That's wonderful! I'm so happy to hear that! 🌟 Keep up the amazing work! Is there anything you'd like to tackle while you're feeling great?"

    # Struggles or negative feelings
    if any(word in message_lower for word in ["tired", "exhausted", "stressed", "couldn't", "didn't", "wasn't able", "failed", "struggled", "hard", "difficult"]):
        return "I hear you, and that sounds really tough. 💜 It's totally okay to have challenging days - you're doing your best, and that's what matters. Sometimes taking a small step or even just taking a break is the right move. Want to talk about it or focus on something manageable?"

    # Frustration or venting
    if any(word in message_lower for word in ["frustrated", "annoying", "ugh", "argh", "why is", "hate"]):
        return "I totally get it - that sounds frustrating! 😤 Sometimes things just don't go our way, and it's okay to feel that way. Want to break things down into smaller steps together, or just need a moment to vent? I'm here either way!"

    # Questions about the agent
    if any(phrase in message_lower for phrase in ["who are you", "what are you", "what can you", "can you help", "what do you do"]):
        return "I'm your personal task assistant and daily companion! 💜 I'm here to help you manage your tasks (add, complete, update, delete), but I'm also here to listen when you need to talk about your day, your feelings, or anything on your mind. Think of me as your friendly productivity buddy who actually cares! ✨"

    # Default friendly response
    return "I'm here with you! 💜 Whether you want to work on tasks or just chat about how things are going, I'm all ears. What's on your mind?"


async def process_request(
    user_id: str,
    message: str,
    conversation_id: Optional[str] = None,
    conversation_history: Optional[list] = None
) -> AgentResponse:
    """
    Process a natural language request - either task operation or casual conversation.

    This is the main entry point for the agent. It:
    1. Determines if the message is casual conversation or task operation
    2. For casual: Responds empathetically and supportively
    3. For tasks: Parses intent, invokes tools, and formats response
    4. Records tool calls to database for context building

    Args:
        user_id: Pre-authenticated user identifier
        message: Natural language message from user
        conversation_id: Optional conversation UUID for tool call tracking
        conversation_history: Optional list of recent messages [{"role": "user"|"assistant", "content": "..."}]

    Returns:
        AgentResponse with natural language response and metadata

    Note:
        The agent is designed to be flexible and understand freestyle instructions
        while also being a supportive companion for daily struggles.
    """
    print(f"Agent process_request received for user ID: {user_id}, message: {message[:50]}...")
    start_time = time.time()

    try:
        # Step 1: Determine if this is casual conversation or task operation
        if is_casual_conversation(message):
            # Handle casual conversation warmly
            response_text = await generate_casual_response(message)
            execution_time_ms = max(1, int((time.time() - start_time) * 1000))

            return AgentResponse(
                response=response_text,
                metadata={
                    "intent": "CASUAL_CONVERSATION",
                    "tool_called": None,
                    "confidence": 1.0,
                    "execution_time_ms": execution_time_ms
                }
            )

        # Step 2: Parse intent and extract parameters for task operations
        intent_classification = parse_intent(message, conversation_history)

        # Step 3: Invoke appropriate MCP tool based on intent
        tool_result = await invoke_tool(user_id, intent_classification, conversation_id)

        # Step 4: Format response
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
            response="Oops, something went wrong on my end! 😅 Could you try that again?",
            metadata={
                "intent": "ERROR",
                "tool_called": None,
                "confidence": 0.0,
                "execution_time_ms": execution_time_ms,
                "error": str(e)
            }
        )


async def invoke_tool(user_id: str, intent: IntentClassification, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Invoke the appropriate MCP tool based on the classified intent.

    Args:
        user_id: User identifier for tool invocation
        intent: Classified intent with extracted parameters
        conversation_id: Optional conversation UUID for tool call tracking

    Returns:
        Dictionary with tool_name, success, data, error, error_code, and tool_call_record

    Note:
        All MCP tools are called synchronously. The async wrapper is for
        future compatibility with async tool implementations.
        Tool calls are NOT saved here - they're saved in chatkit.py after message is created.
    """
    print(f"Agent invoke_tool called for user ID: {user_id}, intent: {intent.operation_type}")
    tool_start_time = time.time()

    try:
        result = None
        if intent.operation_type == Intent.CREATE:
            result = invoke_add_task(user_id, intent.extracted_parameters)
        elif intent.operation_type == Intent.LIST:
            result = invoke_list_tasks(user_id, intent.extracted_parameters)
        elif intent.operation_type == Intent.COMPLETE:
            result = invoke_complete_task(user_id, intent.extracted_parameters)
        elif intent.operation_type == Intent.UPDATE:
            result = invoke_update_task(user_id, intent.extracted_parameters)
        elif intent.operation_type == Intent.DELETE:
            result = invoke_delete_task(user_id, intent.extracted_parameters)
        elif intent.operation_type == Intent.UNKNOWN:
            result = {
                "tool_name": None,
                "success": False,
                "data": None,
                "error": "Unknown intent",
                "error_code": "UNKNOWN_INTENT"
            }
        else:
            result = {
                "tool_name": None,
                "success": False,
                "data": None,
                "error": "Unsupported operation",
                "error_code": "INTERNAL_ERROR"
            }

        # Calculate tool execution time
        execution_time_ms = max(1, int((time.time() - tool_start_time) * 1000))

        # Add execution time to result
        if result:
            result["execution_time_ms"] = execution_time_ms

        return result

    except Exception as e:
        execution_time_ms = int((time.time() - tool_start_time) * 1000)
        return {
            "tool_name": None,
            "success": False,
            "data": None,
            "error": str(e),
            "error_code": "INTERNAL_ERROR",
            "execution_time_ms": execution_time_ms
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
