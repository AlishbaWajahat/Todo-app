# Stateless Task Agent API Documentation

## Overview

The Stateless Task Agent provides a natural language interface for task management. Users can create, list, update, complete, and delete tasks using conversational messages.

## Endpoint

**POST** `/api/v1/agent/chat`

## Authentication

Requires JWT authentication (same as other API endpoints).

## Request Schema

```json
{
  "user_id": "string (required, min 1 char)",
  "message": "string (required, 1-1000 chars)"
}
```

## Response Schema

```json
{
  "response": "string (natural language response)",
  "metadata": {
    "intent": "CREATE | LIST | COMPLETE | UPDATE | DELETE | UNKNOWN",
    "tool_called": "add_task | list_tasks | complete_task | update_task | delete_task | null",
    "confidence": "float (0.0-1.0)",
    "execution_time_ms": "integer"
  }
}
```

## Supported Operations

### 1. Create Task

**Example Messages:**
- "Create a task to buy groceries"
- "Add a high priority task to call dentist by Friday"
- "Remind me to finish the report with detailed analysis"
- "New task: exercise"

**Example Response:**
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

### 2. List Tasks

**Example Messages:**
- "Show me my tasks"
- "What tasks do I have left?" (filters incomplete tasks)
- "Show me high priority tasks" (filters by priority)
- "List my tasks"

**Example Response:**
```json
{
  "response": "You have 3 tasks: 1) Buy groceries 2) Call dentist 3) Finish report",
  "metadata": {
    "intent": "LIST",
    "tool_called": "list_tasks",
    "confidence": 0.98,
    "execution_time_ms": 245
  }
}
```

### 3. Complete Task

**Example Messages:**
- "Mark 'Buy milk' as done"
- "Complete task 5"
- "Undo completion of task 3" (marks as not done)

**Example Response:**
```json
{
  "response": "Marked 'Buy milk' as done",
  "metadata": {
    "intent": "COMPLETE",
    "tool_called": "complete_task",
    "confidence": 0.92,
    "execution_time_ms": 198
  }
}
```

### 4. Update Task

**Example Messages:**
- "Change 'Buy milk' to 'Buy organic milk'"
- "Update task 3 description to include store location"
- "Rename task 5 to 'Call dentist tomorrow'"

**Example Response:**
```json
{
  "response": "Updated 'Buy milk' to 'Buy organic milk'",
  "metadata": {
    "intent": "UPDATE",
    "tool_called": "update_task",
    "confidence": 0.89,
    "execution_time_ms": 223
  }
}
```

### 5. Delete Task

**Example Messages:**
- "Delete 'Old task'"
- "Remove task 2"

**Example Response:**
```json
{
  "response": "Deleted task 'Old task'",
  "metadata": {
    "intent": "DELETE",
    "tool_called": "delete_task",
    "confidence": 0.91,
    "execution_time_ms": 187
  }
}
```

## Error Responses

### Invalid Intent

When the message doesn't match any task operation:

```json
{
  "response": "I can only help with task management. Try 'create a task' or 'show my tasks'.",
  "metadata": {
    "intent": "UNKNOWN",
    "tool_called": null,
    "confidence": 0.45,
    "execution_time_ms": 89
  }
}
```

### Task Not Found

When referencing a non-existent task:

```json
{
  "response": "I couldn't find that task. Try listing your tasks first.",
  "metadata": {
    "intent": "COMPLETE",
    "tool_called": "complete_task",
    "confidence": 0.88,
    "execution_time_ms": 156
  }
}
```

### Validation Error

**HTTP 400** - Invalid request:

```json
{
  "detail": "Message cannot be empty"
}
```

```json
{
  "detail": "Message must be under 1000 characters"
}
```

### Internal Error

**HTTP 500** - Server error:

```json
{
  "detail": "An internal error occurred. Please try again."
}
```

## Error Codes

| Code | Description | User-Friendly Message |
|------|-------------|----------------------|
| `TASK_NOT_FOUND` | Task doesn't exist or user doesn't own it | "I couldn't find that task. Try listing your tasks first." |
| `VALIDATION_ERROR` | Input validation failed | "Invalid input: {details}" |
| `DATABASE_ERROR` | Database operation failed | "Something went wrong. Please try again." |
| `INTERNAL_ERROR` | Unexpected error | "An error occurred. Please try again." |
| `INVALID_USER_ID` | User authentication failed | "User authentication failed. Please log in again." |
| `UNKNOWN_INTENT` | Message doesn't match any operation | "I can only help with task management. Try 'create a task' or 'show my tasks'." |

## Architecture

### Stateless Design

The agent maintains **zero state** between requests:
- No conversation history
- No session management
- No caching
- Each request is processed independently

### Intent Classification

Uses **rule-based pattern matching** (95% of cases):
- Fast response (<100ms for classification)
- Predictable behavior
- High accuracy for common patterns

### Task Identification

Supports two methods:
1. **By ID**: Exact match (e.g., "task 5")
2. **By Title**: Fuzzy match with 70% similarity threshold

### User Isolation

All operations enforce strict user isolation:
- Tasks filtered by `user_id`
- Cross-user access returns `TASK_NOT_FOUND` (not permission denied)
- No information leakage

## Performance

**Target Metrics:**
- Response time: <2 seconds (95th percentile)
- Concurrency: 100+ concurrent requests
- Intent accuracy: 95%+
- Tool invocation accuracy: 98%+

## Testing

See `specs/005-stateless-task-agent/quickstart.md` for:
- Manual testing scenarios
- curl command examples
- Acceptance criteria
- Edge case testing

## Security

- JWT authentication required
- User isolation enforced at query level
- No SQL injection risk (parameterized queries)
- No XSS risk (plain text responses)
- Error messages don't expose internal details
