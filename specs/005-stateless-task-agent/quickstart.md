# Quickstart Guide: Stateless Task Agent with MCP Tool Invocation

**Feature**: 005-stateless-task-agent
**Date**: 2026-02-09
**Purpose**: Testing guide and validation scenarios for the stateless task agent

## Prerequisites

1. **MCP Tools Running**: Ensure 004-mcp-task-tools is implemented and accessible
2. **Database**: Neon PostgreSQL with tasks table populated
3. **Environment Variables**:
   ```bash
   GEMINI_API_KEY=<your-api-key>
   OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
   DATABASE_URL=<neon-connection-string>
   ```
4. **Dependencies Installed**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## Running the Agent

### Start FastAPI Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Verify Agent Endpoint

```bash
curl http://localhost:8000/api/agent/chat
```

Expected: 405 Method Not Allowed (GET not supported, only POST)

## Testing Scenarios

### Scenario 1: Create Task (User Story 1 - P1)

**Test**: Agent interprets "create task" intent and calls add_task MCP tool

**Request**:
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "Create a task to buy groceries"
  }'
```

**Expected Response**:
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

**Validation**:
- ✅ Response is natural language (not JSON)
- ✅ Task appears in database with user_id="test-user-1"
- ✅ Response time < 2 seconds
- ✅ Metadata shows correct intent and tool

**Variations to Test**:
```bash
# With priority
"Add a high priority task to call dentist"

# With due date
"Remind me to finish the report by Friday"

# With description
"Create a task to buy milk with note: get 2% milk"

# Minimal
"New task: exercise"
```

---

### Scenario 2: List Tasks (User Story 2 - P2)

**Test**: Agent interprets "list tasks" intent and calls list_tasks MCP tool

**Setup**: Create 3 tasks for test-user-1 first

**Request**:
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "Show me my tasks"
  }'
```

**Expected Response**:
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

**Validation**:
- ✅ All 3 tasks listed
- ✅ Only test-user-1's tasks shown (user isolation)
- ✅ Response is concise and readable

**Variations to Test**:
```bash
# Filter by completion
"What tasks do I have left?"  # completed=false

# Filter by priority
"Show me high priority tasks"  # priority=high

# Empty list
"List my tasks"  # When user has no tasks
# Expected: "You have no tasks"
```

---

### Scenario 3: Complete Task (User Story 3 - P3)

**Test**: Agent interprets "complete task" intent and calls complete_task MCP tool

**Setup**: Ensure task "Buy groceries" exists for test-user-1

**Request**:
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "Mark Buy groceries as done"
  }'
```

**Expected Response**:
```json
{
  "response": "Marked 'Buy groceries' as done",
  "metadata": {
    "intent": "COMPLETE",
    "tool_called": "complete_task",
    "confidence": 0.92,
    "execution_time_ms": 198
  }
}
```

**Validation**:
- ✅ Task marked as completed in database
- ✅ updated_at timestamp refreshed
- ✅ Response confirms the action

**Variations to Test**:
```bash
# By task ID
"Complete task 5"

# Undo completion
"Mark task 3 as not done"

# Ambiguous reference (multiple matches)
"Mark milk task as done"  # When multiple tasks contain "milk"
# Expected: Clarification request or most recent match
```

---

### Scenario 4: Update Task (User Story 4 - P4)

**Test**: Agent interprets "update task" intent and calls update_task MCP tool

**Setup**: Ensure task "Buy groceries" exists for test-user-1

**Request**:
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "Change Buy groceries to Buy organic groceries"
  }'
```

**Expected Response**:
```json
{
  "response": "Updated 'Buy groceries' to 'Buy organic groceries'",
  "metadata": {
    "intent": "UPDATE",
    "tool_called": "update_task",
    "confidence": 0.89,
    "execution_time_ms": 223
  }
}
```

**Validation**:
- ✅ Task title updated in database
- ✅ updated_at timestamp refreshed
- ✅ Response confirms the change

**Variations to Test**:
```bash
# Update description
"Update task 3 description to include store location"

# Rename by ID
"Rename task 5 to Call dentist tomorrow"
```

---

### Scenario 5: Delete Task (User Story 5 - P5)

**Test**: Agent interprets "delete task" intent and calls delete_task MCP tool

**Setup**: Ensure task "Old task" exists for test-user-1

**Request**:
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "Delete Old task"
  }'
```

**Expected Response**:
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

**Validation**:
- ✅ Task removed from database
- ✅ Task no longer appears in list_tasks
- ✅ Response confirms deletion

**Variations to Test**:
```bash
# By task ID
"Remove task 2"

# Multiple deletions (if supported)
"Delete all completed tasks"
```

---

## Edge Case Testing

### Edge Case 1: Invalid Intent

**Test**: Agent handles non-task-related messages gracefully

**Request**:
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "What is the weather today?"
  }'
```

**Expected Response**:
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

**Validation**:
- ✅ No tool called
- ✅ Helpful guidance provided
- ✅ No error thrown

---

### Edge Case 2: Task Not Found

**Test**: Agent handles TASK_NOT_FOUND error from MCP tool

**Request**:
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "Complete task 9999"
  }'
```

**Expected Response**:
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

**Validation**:
- ✅ Error translated to user-friendly message
- ✅ No technical error details exposed
- ✅ Helpful suggestion provided

---

### Edge Case 3: User Isolation

**Test**: Agent enforces user_id isolation (User A cannot access User B's tasks)

**Setup**:
- Create task "Secret task" for test-user-2
- Try to access it as test-user-1

**Request**:
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "Complete Secret task"
  }'
```

**Expected Response**:
```json
{
  "response": "I couldn't find that task. Try listing your tasks first.",
  "metadata": {
    "intent": "COMPLETE",
    "tool_called": "complete_task",
    "confidence": 0.85,
    "execution_time_ms": 142
  }
}
```

**Validation**:
- ✅ TASK_NOT_FOUND returned (not permission denied)
- ✅ No information leakage about other users' tasks
- ✅ User isolation enforced by MCP tools

---

### Edge Case 4: Stateless Verification

**Test**: Agent maintains zero state between requests

**Steps**:
1. Send request: "Create a task to buy milk"
2. Send request: "What did I just create?" (no context)

**Request 1**:
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "Create a task to buy milk"
  }'
```

**Request 2** (immediately after):
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "What did I just create?"
  }'
```

**Expected Response 2**:
```json
{
  "response": "I can only help with task management. Try 'create a task' or 'show my tasks'.",
  "metadata": {
    "intent": "UNKNOWN",
    "tool_called": null,
    "confidence": 0.42,
    "execution_time_ms": 78
  }
}
```

**Validation**:
- ✅ Agent has no memory of previous request
- ✅ No conversation history maintained
- ✅ Each request processed independently

---

### Edge Case 5: Ambiguous Task Reference

**Test**: Agent handles multiple tasks with similar names

**Setup**: Create tasks "Buy milk" and "Drink milk" for test-user-1

**Request**:
```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "message": "Complete the milk task"
  }'
```

**Expected Response** (one of):
```json
{
  "response": "I found multiple tasks matching 'milk'. Which one? (1) Buy milk (2) Drink milk",
  "metadata": {
    "intent": "COMPLETE",
    "tool_called": null,
    "confidence": 0.65,
    "execution_time_ms": 134
  }
}
```

OR (if using most recent match):
```json
{
  "response": "Marked 'Drink milk' as done",
  "metadata": {
    "intent": "COMPLETE",
    "tool_called": "complete_task",
    "confidence": 0.72,
    "execution_time_ms": 198
  }
}
```

**Validation**:
- ✅ Ambiguity handled gracefully (no crash)
- ✅ Either clarification requested or reasonable assumption made
- ✅ No silent failure

---

## Performance Testing

### Latency Test

**Goal**: Verify <2 second response time (95th percentile)

**Script**:
```bash
# Run 100 requests and measure latency
for i in {1..100}; do
  time curl -X POST http://localhost:8000/api/agent/chat \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": \"test-user-1\", \"message\": \"Show my tasks\"}" \
    -s -o /dev/null
done
```

**Expected**: 95% of requests complete in <2 seconds

---

### Concurrency Test

**Goal**: Verify 100+ concurrent requests supported

**Script** (using Apache Bench):
```bash
ab -n 1000 -c 100 -p request.json -T application/json \
  http://localhost:8000/api/agent/chat
```

**Expected**:
- No errors
- Average response time <2 seconds
- No memory leaks (check with `ps aux | grep uvicorn`)

---

## Validation Checklist

### Functional Requirements

- [ ] FR-001: Agent accepts user_id and user_message
- [ ] FR-002: Agent parses message to identify intent
- [ ] FR-003: Agent extracts parameters from message
- [ ] FR-004: Agent invokes correct MCP tool
- [ ] FR-005: Agent passes user_id to all tool calls
- [ ] FR-006: Agent formats tool responses to natural language
- [ ] FR-007: Agent returns natural language response
- [ ] FR-008: Agent stores no state between requests
- [ ] FR-009: Agent never accesses database directly
- [ ] FR-010: Agent handles ambiguous messages gracefully
- [ ] FR-011: Agent translates error codes to user-friendly messages
- [ ] FR-012: Agent supports task identification by title/ID
- [ ] FR-013: Agent handles non-task messages with guidance
- [ ] FR-014: Agent processes requests independently
- [ ] FR-015: Agent validates parameters before tool calls

### Success Criteria

- [ ] SC-001: 95%+ intent classification accuracy
- [ ] SC-002: 98%+ correct tool invocation rate
- [ ] SC-003: <2 second response time (95th percentile)
- [ ] SC-004: Zero state accumulation (verified over 1000 requests)
- [ ] SC-005: 100% graceful error handling
- [ ] SC-006: Concise responses (<200 chars simple, <500 complex)
- [ ] SC-007: 90%+ parameter extraction accuracy
- [ ] SC-008: 100% ambiguity handling (no crashes)
- [ ] SC-009: User isolation enforced (cross-user access blocked)
- [ ] SC-010: 100% helpful guidance for non-task messages

### Constitution Compliance

- [ ] Stateless Architecture: No state between requests
- [ ] MCP Tool Standards: All operations via MCP tools
- [ ] Agent-Tool Interaction: No direct DB access
- [ ] Code Quality: Minimal files, modular structure

---

## Troubleshooting

### Issue: Agent returns "Internal server error"

**Possible causes**:
1. MCP tools not accessible
2. Database connection failed
3. Gemini API key invalid

**Debug steps**:
```bash
# Check MCP tools
python -c "from mcp.tools.list_tasks import list_tasks; print('OK')"

# Check database
python -c "from core.database import engine; print(engine.url)"

# Check Gemini API
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models
```

---

### Issue: Agent always returns "UNKNOWN" intent

**Possible causes**:
1. Intent parser not working
2. LLM model not responding
3. Classification threshold too high

**Debug steps**:
```bash
# Test intent parser directly
python -c "from agent.intent_parser import parse_intent; print(parse_intent('create a task'))"

# Check LLM connectivity
python -c "from openai import OpenAI; client = OpenAI(api_key='...'); print(client.models.list())"
```

---

### Issue: Slow response times (>2 seconds)

**Possible causes**:
1. Database queries slow
2. LLM API latency high
3. Too many LLM calls (not using rule-based fast path)

**Debug steps**:
```bash
# Check database query time
python -c "import time; from mcp.tools.list_tasks import list_tasks; start = time.time(); list_tasks({'user_id': 'test'}); print(f'{(time.time()-start)*1000}ms')"

# Check LLM latency
curl -w "@curl-format.txt" -H "Authorization: Bearer $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent
```

---

## Notes

- All tests assume MCP tools (004-mcp-task-tools) are already implemented
- User isolation is enforced by MCP tools, not the agent
- Agent is stateless - no setup/teardown needed between tests
- Use different user_ids for isolation testing
- Monitor response times and memory usage during testing
