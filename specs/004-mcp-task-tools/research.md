# Research: MCP Server & Task Tools Implementation

**Feature**: 004-mcp-task-tools
**Date**: 2026-02-09
**Research Phase**: Phase 0 - Discovery

## Research Summary

This document consolidates research findings for implementing an MCP (Model Context Protocol) server with task management tools using the Official MCP SDK for Python.

---

## 1. Official MCP SDK for Python

### Decision: Use `mcp` Python Package

**Package**: `mcp` (Official MCP SDK)
**Installation**: `pip install mcp`

**Rationale**:
- Official SDK ensures protocol compliance
- Provides built-in tool registration and validation
- Handles MCP protocol serialization/deserialization
- Maintained by MCP specification authors

**Server Initialization Pattern**:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Create MCP server instance
server = Server("task-tools-server")

# Register tools
@server.tool()
async def list_tasks(user_id: str) -> dict:
    """List all tasks for a user."""
    # Implementation
    pass

# Run server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)
```

**Key Findings**:
- MCP servers communicate via stdio (standard input/output)
- Tools are registered using decorators or explicit registration
- Server runs asynchronously (async/await pattern)
- Each tool is a Python async function

**Alternatives Considered**:
- Custom MCP implementation: Rejected (violates constraint C-001)
- LangChain MCP adapter: Rejected (adds unnecessary dependency)

---

## 2. MCP Tool Definition with Pydantic Schemas

### Decision: Use Pydantic Models for Input/Output Validation

**Pattern**: Define explicit Pydantic models for each tool's input and output

```python
from pydantic import BaseModel, Field
from typing import Optional, List

# Input schema
class ListTasksInput(BaseModel):
    user_id: str = Field(..., description="Authenticated user ID")
    completed: Optional[bool] = Field(None, description="Filter by completion status")

# Output schema
class ToolResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

# Tool implementation
@server.tool()
async def list_tasks(input: ListTasksInput) -> ToolResponse:
    try:
        # Database query
        tasks = query_tasks(input.user_id, input.completed)
        return ToolResponse(success=True, data={"tasks": tasks})
    except Exception as e:
        return ToolResponse(
            success=False,
            error="Failed to retrieve tasks",
            error_code="DATABASE_ERROR"
        )
```

**Key Findings**:
- Pydantic provides automatic validation before tool execution
- Type hints enable IDE autocomplete and static analysis
- Field descriptions become tool documentation for AI agents
- Validation errors are caught before database operations

**Best Practices**:
- Use `Field(..., description="...")` for all fields (AI agent documentation)
- Make user_id required in all input schemas
- Use Optional[] for nullable fields
- Define max_length constraints for strings (title: 500 chars, description: 2000 chars)

---

## 3. MCP Server Integration with FastAPI

### Decision: Run MCP Server in Separate Process, Share Database

**Pattern**: MCP server runs independently but shares database connection pool

```python
# backend/main.py (FastAPI)
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    create_db_and_tables()
    # MCP server runs separately (not in FastAPI process)
    yield
    # Shutdown: Cleanup

app = FastAPI(lifespan=lifespan)
```

```python
# backend/mcp/server.py (MCP Server - separate process)
from mcp.server import Server
from core.database import engine, get_session

server = Server("task-tools-server")

# Tools use same database engine as FastAPI
@server.tool()
async def list_tasks(input: ListTasksInput) -> ToolResponse:
    with Session(engine) as session:
        # Use shared database connection pool
        tasks = session.exec(select(Task).where(Task.user_id == input.user_id)).all()
        return ToolResponse(success=True, data={"tasks": [t.dict() for t in tasks]})
```

**Key Findings**:
- MCP server runs as separate process (stdio communication)
- Both FastAPI and MCP server import from `core.database` (shared engine)
- Database connection pooling is shared (same engine instance)
- No HTTP communication between FastAPI and MCP server

**Rationale**:
- MCP protocol uses stdio (not HTTP), so separate process is natural
- Shared database engine avoids connection pool exhaustion
- Simpler deployment (both use same DATABASE_URL environment variable)
- Stateless design: MCP server can restart without affecting FastAPI

**Alternatives Considered**:
- Embed MCP server in FastAPI: Rejected (stdio protocol incompatible with HTTP)
- Separate database connections: Rejected (inefficient, connection pool limits)

---

## 4. Error Handling in MCP Tools

### Decision: Structured Error Responses with Error Codes

**Error Response Schema**:

```python
class ToolResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None  # Human-readable message
    error_code: Optional[str] = None  # Machine-readable code
```

**Error Code Taxonomy**:

| Error Code | HTTP Equivalent | Description | Example |
|------------|----------------|-------------|---------|
| INVALID_USER_ID | 400 | user_id missing or invalid format | user_id="" |
| TASK_NOT_FOUND | 404 | Task doesn't exist or user doesn't own it | task_id=999 for user_id=1 |
| VALIDATION_ERROR | 400 | Input validation failed | title exceeds 500 chars |
| DATABASE_ERROR | 500 | Database connection or query failed | Connection timeout |
| INTERNAL_ERROR | 500 | Unexpected error | Unhandled exception |

**Error Handling Pattern**:

```python
@server.tool()
async def add_task(input: AddTaskInput) -> ToolResponse:
    try:
        # Validate user_id
        if not input.user_id or len(input.user_id) == 0:
            return ToolResponse(
                success=False,
                error="User ID is required",
                error_code="INVALID_USER_ID"
            )

        # Validate title length
        if len(input.title) > 500:
            return ToolResponse(
                success=False,
                error="Task title must be 500 characters or less",
                error_code="VALIDATION_ERROR"
            )

        # Database operation
        with Session(engine) as session:
            task = Task(user_id=input.user_id, title=input.title, description=input.description)
            session.add(task)
            session.commit()
            session.refresh(task)

            return ToolResponse(
                success=True,
                data={"task": task.dict()}
            )

    except SQLAlchemyError as e:
        logger.error(f"Database error in add_task: {str(e)}")
        return ToolResponse(
            success=False,
            error="Failed to create task due to database error",
            error_code="DATABASE_ERROR"
        )

    except Exception as e:
        logger.error(f"Unexpected error in add_task: {str(e)}", exc_info=True)
        return ToolResponse(
            success=False,
            error="An unexpected error occurred",
            error_code="INTERNAL_ERROR"
        )
```

**Best Practices**:
- Always return ToolResponse (never raise exceptions to MCP framework)
- Log full error details (including stack traces) for debugging
- Return generic error messages to AI agent (no sensitive information)
- Use specific error codes for programmatic error handling
- Validate inputs before database operations (fail fast)

---

## 5. Stateless Tool Design

### Decision: Pure Functions with No Shared State

**Stateless Design Checklist**:

✅ **DO**:
- Use function parameters for all inputs (no global variables)
- Query database for all data (no in-memory caching)
- Return all results in response (no side effects)
- Use `with Session(engine)` for database access (auto-cleanup)
- Make tools pure functions (same input → same output)

❌ **DON'T**:
- Store state in global variables or class attributes
- Cache query results in memory
- Maintain session state between tool calls
- Use mutable default arguments
- Rely on previous tool call results

**Stateless Tool Template**:

```python
# ✅ GOOD: Stateless tool
@server.tool()
async def list_tasks(input: ListTasksInput) -> ToolResponse:
    # All inputs from parameter
    user_id = input.user_id

    # Query database (no caching)
    with Session(engine) as session:
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()

    # Return all data in response
    return ToolResponse(
        success=True,
        data={"tasks": [t.dict() for t in tasks]}
    )

# ❌ BAD: Stateful tool (DO NOT USE)
task_cache = {}  # Global state - violates stateless principle

@server.tool()
async def list_tasks_bad(input: ListTasksInput) -> ToolResponse:
    # Check cache (stateful)
    if input.user_id in task_cache:
        return ToolResponse(success=True, data={"tasks": task_cache[input.user_id]})

    # Query and cache (stateful)
    with Session(engine) as session:
        tasks = session.exec(select(Task).where(Task.user_id == input.user_id)).all()
        task_cache[input.user_id] = [t.dict() for t in tasks]  # Violates stateless

    return ToolResponse(success=True, data={"tasks": task_cache[input.user_id]})
```

**Verification Techniques**:
- Code review: Search for global variables, class attributes
- Testing: Restart MCP server between test runs (verify no state loss)
- Static analysis: Check for mutable default arguments
- Load testing: Concurrent tool calls should not interfere

**Rationale**:
- Stateless design enables horizontal scaling (multiple MCP server instances)
- Server restart doesn't lose data (all in database)
- Concurrent tool calls don't interfere (no shared state)
- Easier to test (no setup/teardown of state)

---

## Implementation Recommendations

### 1. Module Structure

```
backend/mcp/
├── __init__.py           # Export server instance
├── server.py             # MCP server initialization
├── schemas/              # Pydantic schemas
│   ├── base.py          # ToolResponse
│   ├── task_inputs.py   # Input schemas
│   └── task_outputs.py  # Output schemas (if needed beyond ToolResponse)
└── tools/                # Tool implementations
    ├── list_tasks.py
    ├── add_task.py
    ├── complete_task.py
    ├── update_task.py
    └── delete_task.py
```

### 2. Dependency Installation

Add to `backend/requirements.txt`:
```
mcp>=1.0.0  # Official MCP SDK
```

### 3. Testing Strategy

- **Unit Tests**: Test each tool with mock database
- **Integration Tests**: Test tools with real database (test database)
- **Stateless Verification**: Restart server between tests, verify no data loss
- **Ownership Tests**: Verify user_id isolation (User A cannot access User B's tasks)

### 4. Deployment Considerations

- MCP server runs as separate process: `python -m backend.mcp.server`
- FastAPI runs as usual: `uvicorn backend.main:app`
- Both share DATABASE_URL environment variable
- Both can run in same Docker container (separate processes)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| MCP SDK API changes | High | Pin mcp version in requirements.txt |
| Database connection pool exhaustion | Medium | Share engine between FastAPI and MCP server |
| Concurrent write conflicts | Low | Accept last-write-wins (per spec assumption A-010) |
| Tool call timeout | Medium | Set reasonable database query timeouts |
| Error information leakage | High | Return generic errors, log details server-side |

---

## Next Steps

1. **Phase 1**: Create data-model.md with detailed tool schemas
2. **Phase 1**: Generate contracts/ with JSON schemas for each tool
3. **Phase 1**: Create quickstart.md with testing instructions
4. **Phase 2**: Generate tasks.md with implementation tasks
5. **Implementation**: Use Backend Agent to implement MCP tools
