# Quickstart: Testing MCP Task Tools

**Feature**: 004-mcp-task-tools
**Date**: 2026-02-09
**Phase**: Phase 1 - Design

## Overview

This guide provides instructions for testing the MCP task management tools once implemented. It covers setup, running the MCP server, and testing each tool with example inputs.

---

## Prerequisites

1. **Backend Setup Complete**:
   - PostgreSQL database running (Neon Serverless)
   - Database tables created (tasks, users)
   - Environment variables configured (.env file)

2. **Dependencies Installed**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Test User Created**:
   - Create a test user in the database
   - Note the user_id for testing (e.g., "test-user-123")

---

## Running the MCP Server

### Start MCP Server

```bash
cd backend
python -m mcp.server
```

**Expected Output**:
```
MCP Server initialized: task-tools-server
Registered tools: list_tasks, add_task, complete_task, update_task, delete_task
Server running on stdio...
```

**Note**: The MCP server communicates via stdio (standard input/output), not HTTP. It's designed to be called by AI agents, not directly via curl or Postman.

---

## Testing Tools with MCP Client

### Option 1: Using MCP Inspector (Recommended)

The MCP Inspector is a debugging tool for testing MCP servers.

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector python -m backend.mcp.server
```

This opens a web UI where you can:
- See all registered tools
- View tool schemas
- Call tools with test inputs
- Inspect responses

### Option 2: Using Python Test Script

Create a test script to call MCP tools programmatically:

```python
# test_mcp_tools.py
import asyncio
from mcp.client import Client
from mcp.client.stdio import stdio_client

async def test_list_tasks():
    """Test list_tasks tool."""
    async with stdio_client(["python", "-m", "backend.mcp.server"]) as (read, write):
        client = Client(read, write)

        # Call list_tasks tool
        result = await client.call_tool(
            "list_tasks",
            {"user_id": "test-user-123", "completed": None, "priority": None}
        )

        print("list_tasks result:", result)

if __name__ == "__main__":
    asyncio.run(test_list_tasks())
```

---

## Test Scenarios

### 1. Test list_tasks Tool

**Scenario**: Retrieve all tasks for a user

**Input**:
```json
{
  "user_id": "test-user-123",
  "completed": null,
  "priority": null
}
```

**Expected Success Response**:
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": 1,
        "user_id": "test-user-123",
        "title": "Buy milk",
        "description": "Get 2% milk from store",
        "completed": false,
        "priority": "medium",
        "due_date": "2026-02-10T10:00:00Z",
        "created_at": "2026-02-09T10:00:00Z",
        "updated_at": "2026-02-09T10:00:00Z"
      }
    ],
    "count": 1
  },
  "error": null,
  "error_code": null
}
```

**Test Cases**:
- ✅ List all tasks (no filters)
- ✅ List completed tasks only (completed=true)
- ✅ List incomplete tasks only (completed=false)
- ✅ List tasks by priority (priority="high")
- ✅ Empty result (user has no tasks)
- ❌ Invalid user_id (empty string) → INVALID_USER_ID error

---

### 2. Test add_task Tool

**Scenario**: Create a new task

**Input**:
```json
{
  "user_id": "test-user-123",
  "title": "Buy milk",
  "description": "Get 2% milk from store",
  "priority": "medium",
  "due_date": "2026-02-10T10:00:00Z"
}
```

**Expected Success Response**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 2,
      "user_id": "test-user-123",
      "title": "Buy milk",
      "description": "Get 2% milk from store",
      "completed": false,
      "priority": "medium",
      "due_date": "2026-02-10T10:00:00Z",
      "created_at": "2026-02-09T10:30:00Z",
      "updated_at": "2026-02-09T10:30:00Z"
    }
  },
  "error": null,
  "error_code": null
}
```

**Test Cases**:
- ✅ Create task with all fields
- ✅ Create task with only title (minimal)
- ✅ Create task with description but no priority/due_date
- ❌ Empty title → VALIDATION_ERROR
- ❌ Title >500 characters → VALIDATION_ERROR
- ❌ Description >2000 characters → VALIDATION_ERROR
- ❌ Invalid user_id → INVALID_USER_ID

---

### 3. Test complete_task Tool

**Scenario**: Mark a task as complete

**Input**:
```json
{
  "user_id": "test-user-123",
  "task_id": 1,
  "completed": true
}
```

**Expected Success Response**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 1,
      "user_id": "test-user-123",
      "title": "Buy milk",
      "description": "Get 2% milk from store",
      "completed": true,
      "priority": "medium",
      "due_date": "2026-02-10T10:00:00Z",
      "created_at": "2026-02-09T10:00:00Z",
      "updated_at": "2026-02-09T10:35:00Z"
    }
  },
  "error": null,
  "error_code": null
}
```

**Test Cases**:
- ✅ Mark task as complete (completed=true)
- ✅ Mark task as incomplete (completed=false)
- ✅ Toggle completion status multiple times
- ❌ Task doesn't exist → TASK_NOT_FOUND
- ❌ Task belongs to different user → TASK_NOT_FOUND
- ❌ Invalid task_id (0 or negative) → VALIDATION_ERROR

---

### 4. Test update_task Tool

**Scenario**: Update task title

**Input**:
```json
{
  "user_id": "test-user-123",
  "task_id": 1,
  "new_title": "Buy organic milk",
  "new_description": null
}
```

**Expected Success Response**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 1,
      "user_id": "test-user-123",
      "title": "Buy organic milk",
      "description": "Get 2% milk from store",
      "completed": false,
      "priority": "medium",
      "due_date": "2026-02-10T10:00:00Z",
      "created_at": "2026-02-09T10:00:00Z",
      "updated_at": "2026-02-09T10:40:00Z"
    }
  },
  "error": null,
  "error_code": null
}
```

**Test Cases**:
- ✅ Update title only
- ✅ Update description only
- ✅ Update both title and description
- ❌ Update neither (both null) → VALIDATION_ERROR
- ❌ New title >500 characters → VALIDATION_ERROR
- ❌ New description >2000 characters → VALIDATION_ERROR
- ❌ Task doesn't exist → TASK_NOT_FOUND
- ❌ Task belongs to different user → TASK_NOT_FOUND

---

### 5. Test delete_task Tool

**Scenario**: Delete a task

**Input**:
```json
{
  "user_id": "test-user-123",
  "task_id": 1
}
```

**Expected Success Response**:
```json
{
  "success": true,
  "data": {
    "task_id": 1,
    "deleted": true
  },
  "error": null,
  "error_code": null
}
```

**Test Cases**:
- ✅ Delete existing task
- ✅ Verify task no longer appears in list_tasks
- ❌ Delete non-existent task → TASK_NOT_FOUND
- ❌ Delete task belonging to different user → TASK_NOT_FOUND
- ❌ Delete same task twice → TASK_NOT_FOUND (second attempt)

---

## User Isolation Testing

**Critical Security Test**: Verify users cannot access each other's tasks

### Setup:
1. Create two test users: "user-A" and "user-B"
2. Create tasks for user-A (task IDs: 1, 2, 3)
3. Create tasks for user-B (task IDs: 4, 5, 6)

### Test Cases:

**Test 1: list_tasks isolation**
```json
// User A lists tasks
{"user_id": "user-A", "completed": null, "priority": null}
// Expected: Returns only tasks 1, 2, 3

// User B lists tasks
{"user_id": "user-B", "completed": null, "priority": null}
// Expected: Returns only tasks 4, 5, 6
```

**Test 2: complete_task cross-user attempt**
```json
// User A tries to complete User B's task
{"user_id": "user-A", "task_id": 4, "completed": true}
// Expected: TASK_NOT_FOUND error (not permission denied)
```

**Test 3: update_task cross-user attempt**
```json
// User B tries to update User A's task
{"user_id": "user-B", "task_id": 1, "new_title": "Hacked!", "new_description": null}
// Expected: TASK_NOT_FOUND error
```

**Test 4: delete_task cross-user attempt**
```json
// User A tries to delete User B's task
{"user_id": "user-A", "task_id": 5}
// Expected: TASK_NOT_FOUND error
```

**✅ All cross-user attempts must fail with TASK_NOT_FOUND (not permission denied)**

---

## Stateless Verification Testing

**Test**: Verify MCP server is truly stateless

### Procedure:

1. **Start MCP server**
2. **Create a task** (add_task)
3. **List tasks** (list_tasks) → Verify task appears
4. **Stop MCP server** (Ctrl+C)
5. **Restart MCP server**
6. **List tasks again** (list_tasks) → Verify task still appears

**Expected Result**: Task persists after server restart (data in database, not memory)

### Additional Stateless Tests:

**Test 1: No caching**
- Call list_tasks for user-A
- Manually update task in database (SQL)
- Call list_tasks again for user-A
- Expected: Updated data returned (no stale cache)

**Test 2: Concurrent calls**
- Call add_task for user-A (task 1)
- Simultaneously call add_task for user-B (task 2)
- Both should succeed without interference

---

## Performance Testing

### Latency Benchmarks

**Success Criteria** (from spec):
- MCP server initialization: <2 seconds
- list_tasks (up to 100 tasks): <500ms
- Write operations (add, update, complete, delete): <1 second

### Test Script:

```python
import asyncio
import time
from mcp.client import Client
from mcp.client.stdio import stdio_client

async def benchmark_list_tasks():
    """Benchmark list_tasks performance."""
    async with stdio_client(["python", "-m", "backend.mcp.server"]) as (read, write):
        client = Client(read, write)

        # Warm-up call
        await client.call_tool("list_tasks", {"user_id": "test-user-123"})

        # Benchmark 10 calls
        start = time.time()
        for _ in range(10):
            await client.call_tool("list_tasks", {"user_id": "test-user-123"})
        end = time.time()

        avg_latency = (end - start) / 10
        print(f"Average list_tasks latency: {avg_latency*1000:.2f}ms")

        # Verify <500ms requirement
        assert avg_latency < 0.5, f"Latency {avg_latency*1000:.2f}ms exceeds 500ms limit"

if __name__ == "__main__":
    asyncio.run(benchmark_list_tasks())
```

---

## Troubleshooting

### Issue: MCP server won't start

**Symptoms**: Import errors, module not found

**Solutions**:
- Verify `mcp` package installed: `pip list | grep mcp`
- Check Python path includes backend directory
- Verify all dependencies in requirements.txt installed

### Issue: DATABASE_ERROR responses

**Symptoms**: All tools return DATABASE_ERROR

**Solutions**:
- Check DATABASE_URL environment variable set
- Verify database is running and accessible
- Check database connection pooling configuration
- Review backend logs for detailed error messages

### Issue: TASK_NOT_FOUND for valid tasks

**Symptoms**: Tools return TASK_NOT_FOUND even when task exists

**Solutions**:
- Verify user_id matches task owner in database
- Check task_id is correct (not deleted)
- Review database query logs for WHERE clause

### Issue: Validation errors

**Symptoms**: VALIDATION_ERROR for seemingly valid inputs

**Solutions**:
- Check title length (max 500 characters)
- Check description length (max 2000 characters)
- Verify user_id is non-empty string
- Verify task_id is positive integer

---

## Next Steps

After testing is complete:

1. **Document Test Results**: Record pass/fail for each test case
2. **Performance Metrics**: Document actual latencies vs. requirements
3. **Security Audit**: Verify all user isolation tests passed
4. **Integration Testing**: Test with actual AI agent (OpenAI Agents SDK)
5. **Production Readiness**: Review logs, error handling, monitoring

---

## Additional Resources

- **MCP Specification**: https://modelcontextprotocol.io/
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Tool Contracts**: See `contracts/` directory for JSON schemas
- **Data Model**: See `data-model.md` for detailed schemas
