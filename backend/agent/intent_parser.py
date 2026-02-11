"""
Intent Parser - Rule-based Intent Classification

This module provides rule-based intent classification for natural language
task management messages. It uses keyword patterns to identify user intent
and extract relevant parameters.
"""
import re
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel


class Intent(str, Enum):
    """Task operation intents."""
    CREATE = "CREATE"
    LIST = "LIST"
    COMPLETE = "COMPLETE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    UNKNOWN = "UNKNOWN"


class ClassificationMethod(str, Enum):
    """Method used for intent classification."""
    RULE_BASED = "RULE_BASED"
    LLM_FALLBACK = "LLM_FALLBACK"


class IntentClassification(BaseModel):
    """Result of intent classification."""
    operation_type: Intent
    confidence: float
    extracted_parameters: Dict[str, Any]
    classification_method: ClassificationMethod


def parse_intent(message: str, conversation_history: Optional[list] = None) -> IntentClassification:
    """
    Parse user message to identify intent and extract parameters.

    Uses rule-based keyword matching for fast classification (95% of cases).
    Falls back to LLM for ambiguous cases (future implementation).

    Args:
        message: Natural language message from user
        conversation_history: Optional list of recent messages for context

    Returns:
        IntentClassification with operation type, confidence, and parameters

    Examples:
        >>> parse_intent("Create a task to buy groceries")
        IntentClassification(operation_type=Intent.CREATE, confidence=0.95, ...)

        >>> parse_intent("Show me my tasks")
        IntentClassification(operation_type=Intent.LIST, confidence=0.98, ...)
    """
    message_lower = message.lower().strip()

    # Build context from conversation history for reference extraction
    context_text = ""
    if conversation_history:
        # Get last 3 user messages for context
        recent_user_messages = [
            msg["content"] for msg in conversation_history[-6:]
            if msg.get("role") == "user"
        ][-3:]
        context_text = " ".join(recent_user_messages)

    # Try rule-based classification first (fast path)

    # CREATE patterns (allow optional words like "high priority" between action and "task")
    create_patterns = [
        r'\b(create|add|new)\s+(?:a\s+)?(?:\w+\s+)*task\b',
        r'\bremind\s+me\s+to\b',
        r'\b(make|add)\s+a\s+(?:new\s+)?(?:\w+\s+)?(task|todo|reminder)\b'
    ]
    if any(re.search(pattern, message_lower) for pattern in create_patterns):
        return IntentClassification(
            operation_type=Intent.CREATE,
            confidence=0.95,
            extracted_parameters=_extract_create_params(message),
            classification_method=ClassificationMethod.RULE_BASED
        )

    # LIST patterns (allow optional words like "high priority" before "tasks" and filter words after)
    list_patterns = [
        r'\b(show|list|display|get|view)\s+(?:me\s+)?(?:my\s+)?(?:\w+\s+)*tasks?\b',
        r'\bwhat\s+(?:are\s+)?(?:my\s+)?tasks?\b(?:\s+\w+)*',
        r'\b(see|check)\s+(?:my\s+)?(?:\w+\s+)*tasks?\b'
    ]
    if any(re.search(pattern, message_lower) for pattern in list_patterns):
        return IntentClassification(
            operation_type=Intent.LIST,
            confidence=0.98,
            extracted_parameters=_extract_list_params(message),
            classification_method=ClassificationMethod.RULE_BASED
        )

    # COMPLETE patterns (handle natural language variations)
    complete_patterns = [
        # "mark X as done/complete/completed"
        r'\b(mark|set)\s+.*\s+as\s+(done|complet(?:e|ed)|finish(?:ed)?)\b',
        # "mark X done/complete/completed" (without "as")
        r'\b(mark|set)\s+.*\s+(done|complet(?:e|ed)|finish(?:ed)?)\b',
        # "X task done/complete/finished" (passive)
        r'\btask\s+(done|complet(?:e|ed)|finish(?:ed)?)\b',
        # "complete/finish X"
        r'\b(complet(?:e|ed)|finish(?:ed)?)\s+.*\s+task\b',
        # "done with X"
        r'\bdone\s+with\b',
        # "i already/finished/completed X" followed by mark/done/complete
        r'\b(i\s+already|i\s+finished|i\s+completed|as\s+i\s+already)\b.*\b(mark|done|complet(?:e|ed))\b',
        # Undo completion
        r'\bundo\s+(completion|complet(?:e|ed))\b'
    ]
    if any(re.search(pattern, message_lower) for pattern in complete_patterns):
        return IntentClassification(
            operation_type=Intent.COMPLETE,
            confidence=0.92,
            extracted_parameters=_extract_complete_params(message, context_text),
            classification_method=ClassificationMethod.RULE_BASED
        )

    # UPDATE patterns
    update_patterns = [
        r'\b(change|update|modify|edit|rename)\s+.*\s+to\b',
        r'\bupdate\s+(task|the)\b',
        r'\brename\s+task\b'
    ]
    if any(re.search(pattern, message_lower) for pattern in update_patterns):
        return IntentClassification(
            operation_type=Intent.UPDATE,
            confidence=0.89,
            extracted_parameters=_extract_update_params(message),
            classification_method=ClassificationMethod.RULE_BASED
        )

    # DELETE patterns (allow flexible text after delete/remove)
    delete_patterns = [
        r'\b(delete|remove|get\s+rid\s+of)\s+',  # Match delete/remove followed by anything
        r'\bdelete\s+.*\s+task\b'
    ]
    if any(re.search(pattern, message_lower) for pattern in delete_patterns):
        return IntentClassification(
            operation_type=Intent.DELETE,
            confidence=0.91,
            extracted_parameters=_extract_delete_params(message),
            classification_method=ClassificationMethod.RULE_BASED
        )

    # No pattern matched - return UNKNOWN
    return IntentClassification(
        operation_type=Intent.UNKNOWN,
        confidence=0.45,
        extracted_parameters={},
        classification_method=ClassificationMethod.RULE_BASED
    )


def _extract_create_params(message: str) -> Dict[str, Any]:
    """
    Extract parameters for CREATE intent.

    Extracts: title, description, priority, due_date

    Args:
        message: User message

    Returns:
        Dictionary with extracted parameters
    """
    params = {}

    # Extract title (text after action verb)
    # Simple approach: take everything after "create/add/new task" or "remind me to"
    message_lower = message.lower()

    # Try to find title after common patterns
    title_match = None
    if "remind me to" in message_lower:
        title_match = re.search(r'remind\s+me\s+to\s+(.+)', message_lower, re.IGNORECASE)
    elif "create" in message_lower or "add" in message_lower:
        title_match = re.search(r'(?:create|add|new)\s+(?:a\s+)?task\s+(?:to\s+)?(.+)', message_lower, re.IGNORECASE)

    if title_match:
        title = title_match.group(1).strip()
        # Remove trailing punctuation
        title = re.sub(r'[.!?]+$', '', title)
        params["title"] = title
    else:
        # Fallback: use the whole message
        params["title"] = message.strip()

    # Extract priority (high, medium, low)
    if re.search(r'\bhigh\s+priority\b', message_lower):
        params["priority"] = "high"
    elif re.search(r'\bmedium\s+priority\b', message_lower):
        params["priority"] = "medium"
    elif re.search(r'\blow\s+priority\b', message_lower):
        params["priority"] = "low"
    else:
        params["priority"] = None

    # Extract description (text after "with" or in quotes)
    desc_match = re.search(r'with\s+(.+)', message_lower)
    if desc_match:
        params["description"] = desc_match.group(1).strip()
    else:
        params["description"] = None

    # Extract due_date (basic temporal expressions)
    # This is a placeholder - full implementation in T041
    params["due_date"] = None

    return params


def _extract_list_params(message: str) -> Dict[str, Any]:
    """
    Extract parameters for LIST intent.

    Extracts: completed (filter), priority (filter)

    Args:
        message: User message

    Returns:
        Dictionary with extracted parameters
    """
    params = {}
    message_lower = message.lower()

    # Extract completed filter
    if re.search(r'\b(left|incomplete|not\s+done|pending)\b', message_lower):
        params["completed"] = False
    elif re.search(r'\b(completed|done|finished)\b', message_lower):
        params["completed"] = True
    else:
        params["completed"] = None

    # Extract priority filter
    if re.search(r'\bhigh\s+priority\b', message_lower):
        params["priority"] = "high"
    elif re.search(r'\bmedium\s+priority\b', message_lower):
        params["priority"] = "medium"
    elif re.search(r'\blow\s+priority\b', message_lower):
        params["priority"] = "low"
    else:
        params["priority"] = None

    return params


def _extract_complete_params(message: str, context_text: str = "") -> Dict[str, Any]:
    """
    Extract parameters for COMPLETE intent.

    Extracts: task_id, task_title, completed (status)

    Args:
        message: User message
        context_text: Previous user messages for context extraction

    Returns:
        Dictionary with extracted parameters
    """
    params = {}
    message_lower = message.lower()

    # Extract task_id (number after "task")
    task_id_match = re.search(r'task\s+(\d+)', message_lower)
    if task_id_match:
        params["task_id"] = int(task_id_match.group(1))
    else:
        params["task_id"] = None

    # Extract task_title (multiple strategies for natural language)
    title = None

    # Strategy 1: Text in quotes
    title_match = re.search(r"['\"]([^'\"]+)['\"]", message)
    if title_match:
        title = title_match.group(1)

    # Strategy 2: "mark ... task done/complete" (extract text between mark and task)
    if not title:
        title_match = re.search(r'mark\s+(?:my\s+)?(.+?)\s+task\s+(?:done|complete|finished)', message_lower)
        if title_match:
            title = title_match.group(1).strip()

    # Strategy 3: "mark ... done/complete" (without "task" keyword)
    if not title:
        title_match = re.search(r'mark\s+(?:my\s+)?(.+?)\s+(?:done|complete|finished)', message_lower)
        if title_match:
            title = title_match.group(1).strip()
            # Remove "task" from title if present
            title = re.sub(r'\btask\b', '', title).strip()

    # Strategy 4: "mark ... as done/complete"
    if not title:
        title_match = re.search(r'mark\s+(?:my\s+)?(.+?)\s+as\s+(?:done|complete|finished)', message_lower)
        if title_match:
            title = title_match.group(1).strip()

    # Strategy 5: Extract from context phrases like "i prepared for X mark..."
    if not title:
        # Look for patterns like "i prepared for X" or "i finished X"
        context_match = re.search(r'(?:i\s+(?:prepared|finished|completed|did|studied)\s+(?:for\s+)?(?:my\s+)?(.+?))\s+(?:mark|done|complete)', message_lower)
        if context_match:
            title = context_match.group(1).strip()

    # Strategy 6: Extract from conversation history context
    # If user says "mark it done" or "mark that completed", look at previous messages
    if not title and context_text:
        context_lower = context_text.lower()
        # Check if message has pronouns like "it", "that", "this task"
        has_pronoun = re.search(r'\b(it|that|this(?:\s+task)?)\b', message_lower)
        if has_pronoun:
            # Look for task mentions in recent context: "i did X" or "i bought X" patterns
            context_patterns = [
                r'(?:i\s+(?:did|bought|finished|completed|prepared|studied)\s+(?:for\s+)?(?:my\s+)?(.+?))\s*$',
                r'(?:i\s+(?:went|had)\s+(?:to\s+)?(.+?))\s*$',
                r'(?:just\s+(?:did|finished|completed)\s+(.+?))\s*$'
            ]
            for pattern in context_patterns:
                context_match = re.search(pattern, context_lower)
                if context_match:
                    title = context_match.group(1).strip()
                    # Clean up common endings like "today", "yesterday"
                    title = re.sub(r'\s+(today|yesterday|just now|earlier)$', '', title)
                    break

    # Clean up the title
    if title:
        # Remove possessive "my"
        title = re.sub(r'^my\s+', '', title)
        # Remove "the"
        title = re.sub(r'^the\s+', '', title)
        # Remove trailing "task"
        title = re.sub(r'\s+task$', '', title)
        params["task_title"] = title
    else:
        params["task_title"] = None

    # Extract completion status (default: true, unless "undo")
    if re.search(r'\bundo\b', message_lower):
        params["completed"] = False
    else:
        params["completed"] = True

    return params


def _extract_update_params(message: str) -> Dict[str, Any]:
    """
    Extract parameters for UPDATE intent.

    Extracts: task_id, task_title, new_title, new_description

    Args:
        message: User message

    Returns:
        Dictionary with extracted parameters
    """
    params = {}
    message_lower = message.lower()

    # Extract task_id
    task_id_match = re.search(r'task\s+(\d+)', message_lower)
    if task_id_match:
        params["task_id"] = int(task_id_match.group(1))
    else:
        params["task_id"] = None

    # Extract old and new titles (pattern: "change X to Y")
    change_match = re.search(r"['\"]([^'\"]+)['\"]\s+to\s+['\"]([^'\"]+)['\"]", message)
    if change_match:
        params["task_title"] = change_match.group(1)
        params["new_title"] = change_match.group(2)
    else:
        # Try without quotes
        change_match = re.search(r'(?:change|update|rename)\s+(.+?)\s+to\s+(.+)', message_lower)
        if change_match:
            params["task_title"] = change_match.group(1).strip()
            params["new_title"] = change_match.group(2).strip()
        else:
            params["task_title"] = None
            params["new_title"] = None

    # Extract new description
    desc_match = re.search(r'description\s+to\s+(.+)', message_lower)
    if desc_match:
        params["new_description"] = desc_match.group(1).strip()
    else:
        params["new_description"] = None

    return params


def _extract_delete_params(message: str) -> Dict[str, Any]:
    """
    Extract parameters for DELETE intent.

    Extracts: task_id, task_title

    Args:
        message: User message

    Returns:
        Dictionary with extracted parameters
    """
    params = {}
    message_lower = message.lower()

    # Extract task_id
    task_id_match = re.search(r'task\s+(\d+)', message_lower)
    if task_id_match:
        params["task_id"] = int(task_id_match.group(1))
    else:
        params["task_id"] = None

    # Extract task_title (text in quotes or after "delete/remove")
    title_match = re.search(r"['\"]([^'\"]+)['\"]", message)
    if title_match:
        params["task_title"] = title_match.group(1)
    else:
        # Try to extract title after "delete/remove"
        title_match = re.search(r'(?:delete|remove)\s+(.+)$', message_lower)
        if title_match:
            title = title_match.group(1).strip()
            # Remove "the" and "task" from the beginning (in any order)
            while title.startswith("the ") or title.startswith("task "):
                if title.startswith("the "):
                    title = title[4:].strip()  # Remove "the "
                elif title.startswith("task "):
                    title = title[5:].strip()  # Remove "task "
            params["task_title"] = title
        else:
            params["task_title"] = None

    return params
