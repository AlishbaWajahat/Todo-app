# Data Model: Stateless Task Agent with MCP Tool Invocation

**Feature**: 005-stateless-task-agent
**Date**: 2026-02-09
**Purpose**: Define conceptual entities and their relationships for the stateless task agent

## Overview

This feature introduces a stateless AI agent that processes natural language requests. The entities defined here are **conceptual models** for internal processing, not database tables. The agent maintains zero persistent state - all task data is managed by MCP tools.

## Conceptual Entities

### AgentRequest

Represents a single user request to the agent.

**Attributes**:
- `user_id` (string, required): Pre-authenticated user identifier
- `message` (string, required): Natural language message from user (max 1000 characters)
- `timestamp` (datetime, optional): Request timestamp for logging

**Validation Rules**:
- `user_id` must be non-empty string
- `message` must be 1-1000 characters
- `message` must be plain text (no HTML, no special characters)

**Lifecycle**: Created per request, discarded after response

**Example**:
```json
{
  "user_id": "user-123",
  "message": "Create a task to buy groceries",
  "timestamp": "2026-02-09T10:30:00Z"
}
```

---

### IntentClassification

Represents the classified intent and extracted parameters from user message.

**Attributes**:
- `operation_type` (enum, required): One of [CREATE, LIST, COMPLETE, UPDATE, DELETE]
- `confidence` (float, required): Classification confidence score (0.0-1.0)
- `extracted_parameters` (dict, required): Parameters extracted from message
- `classification_method` (enum, required): One of [RULE_BASED, LLM_FALLBACK]

**Extracted Parameters by Operation**:

**CREATE**:
- `title` (string, required): Task title
- `description` (string, optional): Task description
- `priority` (string, optional): One of [low, medium, high]
- `due_date` (datetime, optional): Task due date

**LIST**:
- `completed` (boolean, optional): Filter by completion status
- `priority` (string, optional): Filter by priority

**COMPLETE**:
- `task_id` (int, optional): Task ID if specified
- `task_title` (string, optional): Task title for fuzzy matching
- `completed` (boolean, required): New completion status

**UPDATE**:
- `task_id` (int, optional): Task ID if specified
- `task_title` (string, optional): Task title for fuzzy matching
- `new_title` (string, optional): New task title
- `new_description` (string, optional): New task description

**DELETE**:
- `task_id` (int, optional): Task ID if specified
- `task_title` (string, optional): Task title for fuzzy matching

**Validation Rules**:
- `confidence` must be >= 0.7 for automatic execution
- If confidence < 0.7, request clarification from user
- At least one parameter must be extracted for each operation

**Lifecycle**: Created during intent parsing, used for tool invocation, discarded after response

**Example**:
```json
{
  "operation_type": "CREATE",
  "confidence": 0.95,
  "extracted_parameters": {
    "title": "Buy groceries",
    "description": null,
    "priority": null,
    "due_date": null
  },
  "classification_method": "RULE_BASED"
}
```

---

### ToolInvocation

Represents a call to an MCP tool and its result.

**Attributes**:
- `tool_name` (string, required): Name of MCP tool called
- `input_parameters` (dict, required): Parameters passed to tool
- `output_result` (dict, required): Tool response (ToolResponse format)
- `execution_time_ms` (int, required): Tool execution time in milliseconds
- `success` (boolean, required): Whether tool call succeeded

**Tool Names**:
- `list_tasks`: Retrieve user's tasks
- `add_task`: Create new task
- `complete_task`: Toggle task completion
- `update_task`: Update task details
- `delete_task`: Delete task

**Input Parameters**:
All tools require `user_id` plus operation-specific parameters (see MCP tool schemas in 004-mcp-task-tools).

**Output Result**:
All tools return `ToolResponse` format:
```json
{
  "success": boolean,
  "data": object | null,
  "error": string | null,
  "error_code": string | null
}
```

**Validation Rules**:
- `tool_name` must match one of the 5 MCP tools
- `input_parameters` must include `user_id`
- `output_result` must follow ToolResponse schema

**Lifecycle**: Created during tool invocation, used for response formatting, discarded after response

**Example**:
```json
{
  "tool_name": "add_task",
  "input_parameters": {
    "user_id": "user-123",
    "title": "Buy groceries",
    "description": null,
    "priority": null,
    "due_date": null
  },
  "output_result": {
    "success": true,
    "data": {
      "task": {
        "id": 42,
        "title": "Buy groceries",
        "completed": false,
        "created_at": "2026-02-09T10:30:00Z"
      }
    },
    "error": null,
    "error_code": null
  },
  "execution_time_ms": 245,
  "success": true
}
```

---

### AgentResponse

Represents the agent's response to the user.

**Attributes**:
- `response` (string, required): Natural language response to user
- `metadata` (dict, optional): Additional context for debugging/logging

**Metadata Fields**:
- `intent` (string): Classified intent
- `tool_called` (string): MCP tool invoked
- `confidence` (float): Classification confidence
- `execution_time_ms` (int): Total request processing time

**Validation Rules**:
- `response` must be 1-500 characters (concise)
- `response` must be plain text (no JSON, no HTML)
- `response` must be user-friendly (no technical jargon)

**Response Patterns**:

**Success**:
- CREATE: "Task created: {title}"
- LIST: "You have {count} tasks: {list}"
- COMPLETE: "Marked '{title}' as {done/not done}"
- UPDATE: "Updated '{old_title}' to '{new_title}'"
- DELETE: "Deleted task '{title}'"

**Error**:
- Invalid intent: "I can only help with task management. Try 'create a task' or 'show my tasks'."
- Missing parameters: "I need more details. What should the task be called?"
- Tool error: "I couldn't find that task. Try listing your tasks first."

**Lifecycle**: Created after tool invocation, returned to user, discarded

**Example**:
```json
{
  "response": "Task created: Buy groceries",
  "metadata": {
    "intent": "CREATE",
    "tool_called": "add_task",
    "confidence": 0.95,
    "execution_time_ms": 312
  }
}
```

## Entity Relationships

```
AgentRequest
    ↓ (parsed by intent_parser)
IntentClassification
    ↓ (used to invoke tool)
ToolInvocation
    ↓ (formatted by response_formatter)
AgentResponse
```

**Flow**:
1. User sends `AgentRequest` (user_id + message)
2. Agent parses message → `IntentClassification` (operation + parameters)
3. Agent invokes MCP tool → `ToolInvocation` (tool call + result)
4. Agent formats result → `AgentResponse` (natural language)
5. All entities discarded (stateless)

## State Management

**CRITICAL**: This agent is **stateless**. All entities are:
- Created per request
- Exist only in memory during request processing
- Discarded after response is sent
- Never persisted to database or cache

**No State Between Requests**:
- No conversation history
- No user context (except user_id)
- No session management
- No caching of intents or responses

**Data Persistence**:
All task data is managed by MCP tools (004-mcp-task-tools), which persist to PostgreSQL database. The agent never accesses the database directly.

## Validation Summary

| Entity | Required Fields | Optional Fields | Max Size |
|--------|----------------|-----------------|----------|
| AgentRequest | user_id, message | timestamp | message: 1000 chars |
| IntentClassification | operation_type, confidence, extracted_parameters, classification_method | - | - |
| ToolInvocation | tool_name, input_parameters, output_result, execution_time_ms, success | - | - |
| AgentResponse | response | metadata | response: 500 chars |

## Error Handling

**Validation Errors**:
- Invalid user_id → HTTP 400 "User ID is required"
- Empty message → HTTP 400 "Message cannot be empty"
- Message too long → HTTP 400 "Message must be under 1000 characters"

**Classification Errors**:
- Low confidence (<0.7) → Request clarification from user
- No intent matched → "I can only help with task management"
- Ambiguous parameters → Ask for clarification

**Tool Errors**:
- TASK_NOT_FOUND → "I couldn't find that task"
- VALIDATION_ERROR → "Invalid input: {details}"
- DATABASE_ERROR → "Something went wrong. Please try again."
- INTERNAL_ERROR → "An error occurred. Please try again."

## Notes

- All entities are Python dataclasses or Pydantic models (not database tables)
- Entity lifecycle is request-scoped (created and destroyed per request)
- No ORM mappings needed (agent doesn't access database)
- Validation enforced at API layer (FastAPI + Pydantic)
