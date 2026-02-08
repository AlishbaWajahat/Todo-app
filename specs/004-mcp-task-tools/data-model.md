# Data Model: MCP Task Tools

**Feature**: 004-mcp-task-tools
**Date**: 2026-02-09
**Phase**: Phase 1 - Design

## Overview

This document defines the data structures, schemas, and entities used by the MCP task management tools. All schemas use Pydantic for validation and are designed to be stateless, with explicit input/output contracts.

---

## Core Entities

### 1. Task (Database Entity)

**Source**: Existing `backend/models/task.py` (REUSE - no modifications)

```python
class Task(SQLModel, table=True):
    """Task entity - represents a todo item belonging to a specific user."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    priority: Optional[str] = Field(default=None, max_length=20)
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Key Attributes**:
- `id`: Auto-generated primary key
- `user_id`: Owner of the task (enforces isolation)
- `title`: Required, 1-200 characters
- `description`: Optional, max 2000 characters
- `completed`: Boolean flag, default False
- `created_at`, `updated_at`: Automatic timestamps

**Validation Rules**:
- Title: 1-500 characters (MCP tools will enforce 500 char limit, stricter than model's 200)
- Description: 0-2000 characters
- user_id: Required, non-empty string

---

## MCP Tool Schemas

### Base Response Schema

**Purpose**: Standard response format for all MCP tools

```python
class ToolResponse(BaseModel):
    """
    Standard response format for all MCP tools.

    Ensures consistent error handling and data structure across all tools.
    """
    success: bool = Field(..., description="Whether the operation succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data (present on success)")
    error: Optional[str] = Field(None, description="Human-readable error message (present on failure)")
    error_code: Optional[str] = Field(None, description="Machine-readable error code (present on failure)")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "success": True,
                    "data": {"task": {"id": 1, "title": "Buy milk", "completed": False}},
                    "error": None,
                    "error_code": None
                },
                {
                    "success": False,
                    "data": None,
                    "error": "Task not found or you don't have permission to access it",
                    "error_code": "TASK_NOT_FOUND"
                }
            ]
        }
```

**Error Codes**:
- `INVALID_USER_ID`: user_id is missing, empty, or invalid format
- `TASK_NOT_FOUND`: Task doesn't exist or user doesn't own it
- `VALIDATION_ERROR`: Input validation failed (title too long, etc.)
- `DATABASE_ERROR`: Database connection or query failed
- `INTERNAL_ERROR`: Unexpected error occurred

---

## Tool Input Schemas

### 1. ListTasksInput

**Tool**: `list_tasks`
**Purpose**: Retrieve all tasks for a user with optional filtering

```python
class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""
    user_id: str = Field(..., description="Authenticated user ID (required)", min_length=1)
    completed: Optional[bool] = Field(None, description="Filter by completion status (optional)")
    priority: Optional[str] = Field(None, description="Filter by priority: low, medium, high (optional)")

    class Config:
        json_schema_extra = {
            "examples": [
                {"user_id": "user123", "completed": None, "priority": None},
                {"user_id": "user123", "completed": True, "priority": "high"}
            ]
        }
```

**Validation Rules**:
- `user_id`: Required, non-empty string
- `completed`: Optional boolean (None = no filter)
- `priority`: Optional string (None = no filter)

---

### 2. AddTaskInput

**Tool**: `add_task`
**Purpose**: Create a new task for a user

```python
class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""
    user_id: str = Field(..., description="Authenticated user ID (required)", min_length=1)
    title: str = Field(..., description="Task title (required)", min_length=1, max_length=500)
    description: Optional[str] = Field(None, description="Task description (optional)", max_length=2000)
    priority: Optional[str] = Field(None, description="Task priority: low, medium, high (optional)")
    due_date: Optional[datetime] = Field(None, description="Task due date in ISO 8601 format (optional)")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "user_id": "user123",
                    "title": "Buy milk",
                    "description": "Get 2% milk from store",
                    "priority": "medium",
                    "due_date": "2026-02-10T10:00:00Z"
                },
                {
                    "user_id": "user123",
                    "title": "Call dentist",
                    "description": None,
                    "priority": None,
                    "due_date": None
                }
            ]
        }
```

**Validation Rules**:
- `user_id`: Required, non-empty string
- `title`: Required, 1-500 characters
- `description`: Optional, max 2000 characters
- `priority`: Optional, one of: "low", "medium", "high"
- `due_date`: Optional, ISO 8601 datetime

---

### 3. CompleteTaskInput

**Tool**: `complete_task`
**Purpose**: Mark a task as complete or incomplete

```python
class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""
    user_id: str = Field(..., description="Authenticated user ID (required)", min_length=1)
    task_id: int = Field(..., description="Task ID to update (required)", gt=0)
    completed: bool = Field(..., description="New completion status (required)")

    class Config:
        json_schema_extra = {
            "examples": [
                {"user_id": "user123", "task_id": 1, "completed": True},
                {"user_id": "user123", "task_id": 2, "completed": False}
            ]
        }
```

**Validation Rules**:
- `user_id`: Required, non-empty string
- `task_id`: Required, positive integer
- `completed`: Required boolean

---

### 4. UpdateTaskInput

**Tool**: `update_task`
**Purpose**: Update task title and/or description

```python
class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    user_id: str = Field(..., description="Authenticated user ID (required)", min_length=1)
    task_id: int = Field(..., description="Task ID to update (required)", gt=0)
    new_title: Optional[str] = Field(None, description="New task title (optional)", min_length=1, max_length=500)
    new_description: Optional[str] = Field(None, description="New task description (optional)", max_length=2000)

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        """Ensure at least one field is being updated."""
        if self.new_title is None and self.new_description is None:
            raise ValueError("At least one of new_title or new_description must be provided")
        return self

    class Config:
        json_schema_extra = {
            "examples": [
                {"user_id": "user123", "task_id": 1, "new_title": "Buy organic milk", "new_description": None},
                {"user_id": "user123", "task_id": 2, "new_title": None, "new_description": "Updated description"},
                {"user_id": "user123", "task_id": 3, "new_title": "New title", "new_description": "New description"}
            ]
        }
```

**Validation Rules**:
- `user_id`: Required, non-empty string
- `task_id`: Required, positive integer
- `new_title`: Optional, 1-500 characters (if provided)
- `new_description`: Optional, max 2000 characters (if provided)
- **At least one of new_title or new_description must be provided**

---

### 5. DeleteTaskInput

**Tool**: `delete_task`
**Purpose**: Permanently delete a task

```python
class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""
    user_id: str = Field(..., description="Authenticated user ID (required)", min_length=1)
    task_id: int = Field(..., description="Task ID to delete (required)", gt=0)

    class Config:
        json_schema_extra = {
            "examples": [
                {"user_id": "user123", "task_id": 1}
            ]
        }
```

**Validation Rules**:
- `user_id`: Required, non-empty string
- `task_id`: Required, positive integer

---

## Tool Output Data Structures

### Task Dictionary Format

**Purpose**: Standard format for returning task data in ToolResponse.data

```python
{
    "id": 1,
    "user_id": "user123",
    "title": "Buy milk",
    "description": "Get 2% milk from store",
    "completed": False,
    "priority": "medium",
    "due_date": "2026-02-10T10:00:00Z",
    "created_at": "2026-02-09T10:00:00Z",
    "updated_at": "2026-02-09T10:00:00Z"
}
```

**Conversion**: Use `task.dict()` or `task.model_dump()` to convert SQLModel Task to dictionary

---

### Tool-Specific Response Data

#### list_tasks Response Data

```python
{
    "tasks": [
        {
            "id": 1,
            "user_id": "user123",
            "title": "Buy milk",
            "description": "Get 2% milk from store",
            "completed": False,
            "priority": "medium",
            "due_date": "2026-02-10T10:00:00Z",
            "created_at": "2026-02-09T10:00:00Z",
            "updated_at": "2026-02-09T10:00:00Z"
        },
        {
            "id": 2,
            "user_id": "user123",
            "title": "Call dentist",
            "description": None,
            "completed": True,
            "priority": None,
            "due_date": None,
            "created_at": "2026-02-08T10:00:00Z",
            "updated_at": "2026-02-09T09:00:00Z"
        }
    ],
    "count": 2
}
```

#### add_task Response Data

```python
{
    "task": {
        "id": 3,
        "user_id": "user123",
        "title": "Buy milk",
        "description": "Get 2% milk from store",
        "completed": False,
        "priority": "medium",
        "due_date": "2026-02-10T10:00:00Z",
        "created_at": "2026-02-09T10:30:00Z",
        "updated_at": "2026-02-09T10:30:00Z"
    }
}
```

#### complete_task Response Data

```python
{
    "task": {
        "id": 1,
        "user_id": "user123",
        "title": "Buy milk",
        "description": "Get 2% milk from store",
        "completed": True,  # Updated field
        "priority": "medium",
        "due_date": "2026-02-10T10:00:00Z",
        "created_at": "2026-02-09T10:00:00Z",
        "updated_at": "2026-02-09T10:35:00Z"  # Updated timestamp
    }
}
```

#### update_task Response Data

```python
{
    "task": {
        "id": 1,
        "user_id": "user123",
        "title": "Buy organic milk",  # Updated field
        "description": "Get 2% milk from store",
        "completed": False,
        "priority": "medium",
        "due_date": "2026-02-10T10:00:00Z",
        "created_at": "2026-02-09T10:00:00Z",
        "updated_at": "2026-02-09T10:40:00Z"  # Updated timestamp
    }
}
```

#### delete_task Response Data

```python
{
    "task_id": 1,
    "deleted": True
}
```

---

## Database Query Patterns

### User Isolation Pattern

**All queries MUST filter by user_id to enforce ownership:**

```python
# ✅ CORRECT: Filter by user_id
statement = select(Task).where(Task.user_id == input.user_id)

# ❌ INCORRECT: No user_id filter (security violation)
statement = select(Task)  # Returns all users' tasks!
```

### Ownership Verification Pattern

**For update/delete operations, verify task exists AND belongs to user:**

```python
# Query with user_id filter
task = session.exec(
    select(Task).where(Task.id == input.task_id, Task.user_id == input.user_id)
).first()

if not task:
    # Task doesn't exist OR user doesn't own it
    return ToolResponse(
        success=False,
        error="Task not found or you don't have permission to access it",
        error_code="TASK_NOT_FOUND"
    )
```

**Security Note**: Return "TASK_NOT_FOUND" (not "PERMISSION_DENIED") to prevent information leakage about task existence.

---

## State Management

### Stateless Design Principles

1. **No Global State**: All data comes from function parameters
2. **No Caching**: Query database on every tool call
3. **No Session State**: Each tool call is independent
4. **Database is Source of Truth**: All state persisted to PostgreSQL

### Session Management Pattern

```python
# ✅ CORRECT: Use context manager (auto-cleanup)
with Session(engine) as session:
    task = session.exec(select(Task).where(Task.id == task_id)).first()
    # Session automatically closed after block

# ❌ INCORRECT: Manual session management (can leak connections)
session = Session(engine)
task = session.exec(select(Task).where(Task.id == task_id)).first()
session.close()  # Easy to forget or skip on error
```

---

## Validation Summary

### Input Validation Checklist

- ✅ user_id: Non-empty string (all tools)
- ✅ task_id: Positive integer (update, complete, delete tools)
- ✅ title: 1-500 characters (add, update tools)
- ✅ description: 0-2000 characters (add, update tools)
- ✅ completed: Boolean (complete tool)
- ✅ At least one field provided (update tool)

### Output Validation Checklist

- ✅ success: Always present (boolean)
- ✅ data: Present on success, contains expected structure
- ✅ error: Present on failure, human-readable message
- ✅ error_code: Present on failure, machine-readable code
- ✅ Timestamps: ISO 8601 format
- ✅ No sensitive information in error messages

---

## Next Steps

1. Generate JSON schema contracts in `contracts/` directory
2. Create quickstart.md with testing examples
3. Update agent context with MCP technology
4. Generate tasks.md for implementation
