# Research: Stateless Task Agent with MCP Tool Invocation

**Feature**: 005-stateless-task-agent
**Date**: 2026-02-09
**Purpose**: Document technical decisions, alternatives considered, and rationale for implementation approach

## Technical Decisions

### Decision 1: OpenAI Agent SDK with Gemini Routing

**What was chosen**: Use OpenAI Agent SDK with `OpenAIChatCompletionModel` configured to route requests through Gemini API via OpenAI-compatible interface.

**Rationale**:
- OpenAI Agent SDK provides structured agent framework with built-in tool calling
- Gemini offers competitive pricing and performance for intent classification
- OpenAI-compatible interface allows easy model swapping without code changes
- Agent SDK handles tool registration, invocation, and response formatting automatically

**Alternatives considered**:
1. **Direct Gemini SDK**: Would require custom tool calling implementation, more boilerplate
2. **LangChain**: Heavier framework with unnecessary features (memory, chains) that violate stateless requirement
3. **Custom LLM integration**: More control but significantly more development time and maintenance

**Trade-offs**:
- Pro: Faster development, proven patterns, easy model switching
- Con: Dependency on OpenAI SDK abstractions, potential vendor lock-in
- Mitigation: OpenAI-compatible interface allows model provider changes

### Decision 2: Rule-Based Intent Classification with LLM Fallback

**What was chosen**: Deterministic keyword/pattern matching for common intents, with LLM fallback for ambiguous cases.

**Rationale**:
- 95% of user messages follow predictable patterns ("create task", "show my tasks", "mark X as done")
- Rule-based classification is faster (<10ms) and more predictable than pure LLM
- LLM fallback handles edge cases and natural language variations
- Reduces API costs by avoiding LLM calls for simple intents

**Alternatives considered**:
1. **Pure LLM classification**: More flexible but slower (100-500ms), higher cost, less predictable
2. **Pure rule-based**: Faster but brittle, fails on natural language variations
3. **Fine-tuned classifier**: Requires training data, maintenance overhead, overkill for 5 intents

**Implementation approach**:
```python
# Pseudo-code
def classify_intent(message):
    # Try rule-based first (fast path)
    if matches_create_pattern(message):
        return Intent.CREATE
    elif matches_list_pattern(message):
        return Intent.LIST
    # ... other patterns

    # Fallback to LLM for ambiguous cases
    return llm_classify(message)
```

### Decision 3: Minimal File Structure (3 Files)

**What was chosen**: Three-file architecture for agent logic:
1. `agent.py` - Agent initialization and request handling
2. `intent_parser.py` - Intent classification and parameter extraction
3. `response_formatter.py` - Tool output to natural language conversion

**Rationale**:
- Clear separation of concerns (parsing, invocation, formatting)
- Easy to test each component independently
- Minimal complexity while maintaining modularity
- Follows constitution requirement for minimal files

**Alternatives considered**:
1. **Single file**: Simpler but harder to test, violates separation of concerns
2. **More granular (5+ files)**: Over-engineering for a stateless agent, violates minimal file requirement
3. **Class-based architecture**: More OOP but adds unnecessary abstraction for stateless functions

### Decision 4: FastAPI Endpoint Integration

**What was chosen**: Add agent endpoint to existing FastAPI application at `/api/agent/chat`.

**Rationale**:
- Reuses existing FastAPI infrastructure (auth, middleware, error handling)
- Consistent with existing API patterns in the application
- Easy to integrate with frontend or external clients
- Supports async request handling for concurrent users

**Endpoint design**:
```python
POST /api/agent/chat
Request: {
    "user_id": "string",
    "message": "string"
}
Response: {
    "response": "string",
    "metadata": {
        "intent": "string",
        "tool_called": "string",
        "confidence": float
    }
}
```

### Decision 5: MCP Tool Integration Pattern

**What was chosen**: Import and invoke MCP tools directly from `backend/mcp/tools/` module.

**Rationale**:
- MCP tools are already implemented and tested (004-mcp-task-tools)
- Direct function calls are faster than HTTP/RPC overhead
- Maintains stateless architecture (tools are stateless functions)
- Simplifies error handling (Python exceptions vs HTTP errors)

**Alternatives considered**:
1. **HTTP calls to MCP server**: Adds network latency, requires MCP server to be running
2. **Message queue**: Over-engineering for synchronous operations
3. **Shared library**: Current approach (direct imports) is effectively this

**Integration pattern**:
```python
from mcp.tools.list_tasks import list_tasks
from mcp.tools.add_task import add_task
# ... other tools

def invoke_tool(intent, params):
    if intent == Intent.LIST:
        return list_tasks(params)
    elif intent == Intent.CREATE:
        return add_task(params)
    # ... other tools
```

### Decision 6: Stateless Architecture Enforcement

**What was chosen**: Pure functions with no global state, no class instances, no caching.

**Rationale**:
- Aligns with constitution Principle VII (Stateless Architecture)
- Enables horizontal scaling without session affinity
- Simplifies testing (no setup/teardown of state)
- Ensures server restart resilience (no in-memory data loss)

**Implementation guidelines**:
- All functions are pure (same input → same output)
- No module-level variables (except constants)
- No class instances with mutable state
- Database queries via MCP tools (stateless, DB-backed)

**Verification**:
```python
# Good: Pure function
def parse_intent(message: str) -> Intent:
    return classify(message)

# Bad: Stateful class
class Agent:
    def __init__(self):
        self.history = []  # ❌ State!
```

## Best Practices

### OpenAI Agent SDK Usage

**Key patterns**:
1. Initialize agent once at module load (not per request)
2. Register MCP tools as agent functions with explicit schemas
3. Use async/await for non-blocking I/O
4. Handle tool errors gracefully (return ToolResponse with error)

**Example**:
```python
from openai_agents import Agent
from openai import OpenAI

# Initialize once (module-level)
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

agent = Agent(
    model="gemini-1.5-flash",
    tools=[list_tasks_tool, add_task_tool, ...]
)

# Use per request
async def handle_request(user_id: str, message: str):
    response = await agent.run(message, context={"user_id": user_id})
    return format_response(response)
```

### Intent Classification Patterns

**Common patterns to match**:
- Create: "create", "add", "new task", "remind me to"
- List: "show", "list", "what are my", "display"
- Complete: "done", "finished", "complete", "mark as"
- Update: "change", "update", "modify", "rename"
- Delete: "delete", "remove", "get rid of"

**Parameter extraction**:
- Task title: Extract quoted text or text after action verb
- Priority: Match "high", "medium", "low" keywords
- Due date: Parse temporal expressions ("tomorrow", "Friday", "next week")
- Task ID: Extract numbers after "task" keyword

### Error Handling Strategy

**Error types and responses**:
1. **Invalid intent**: "I can only help with task management. Try 'create a task' or 'show my tasks'."
2. **Missing parameters**: "I need more details. What should the task be called?"
3. **Tool error (TASK_NOT_FOUND)**: "I couldn't find that task. Try listing your tasks first."
4. **Tool error (DATABASE_ERROR)**: "Something went wrong. Please try again."
5. **Ambiguous reference**: "I found multiple tasks matching 'milk'. Which one? (1) Buy milk (2) Drink milk"

## Performance Considerations

### Latency Budget

**Target: <2 seconds (95th percentile)**

Breakdown:
- Intent classification: <100ms (rule-based) or <500ms (LLM fallback)
- MCP tool invocation: <500ms (database query)
- Response formatting: <50ms (string formatting)
- Network overhead: <500ms (API request/response)
- Buffer: 350ms

**Optimization strategies**:
1. Use rule-based classification for common intents (fast path)
2. Async/await for concurrent operations
3. Connection pooling for database (via MCP tools)
4. Minimal response formatting (no complex NLG)

### Concurrency

**Target: 100+ concurrent requests**

Approach:
- FastAPI async endpoints (non-blocking I/O)
- Stateless design (no locking, no shared state)
- Database connection pooling (handled by MCP tools)
- Horizontal scaling (multiple instances)

## Security Considerations

### User Isolation

**Enforcement**:
- user_id passed to all MCP tool calls
- MCP tools filter all queries by user_id
- No cross-user data leakage possible

**Verification**:
- Test with multiple user_ids
- Verify User A cannot access User B's tasks
- Check all tool calls include user_id parameter

### Input Validation

**Validation layers**:
1. FastAPI request validation (Pydantic schemas)
2. Intent parser validation (message length, format)
3. MCP tool validation (parameter types, ranges)

**Sanitization**:
- No SQL injection risk (MCP tools use parameterized queries)
- No XSS risk (plain text responses, no HTML)
- No command injection risk (no shell commands)

## Testing Strategy

### Unit Tests

**Coverage targets**:
- Intent parser: 95% coverage (all intent patterns, edge cases)
- Response formatter: 90% coverage (all tool outputs, error cases)
- Agent integration: 85% coverage (happy paths, error paths)

**Test fixtures**:
- Mock MCP tool responses (success and error cases)
- Sample user messages (diverse phrasings)
- Expected intent classifications and parameters

### Integration Tests

**Scenarios**:
1. End-to-end: User message → Intent → Tool call → Response
2. Error handling: Tool errors → User-friendly messages
3. Ambiguity: Multiple matches → Clarification request
4. Statelessness: Multiple requests → No state accumulation

### Manual Testing

**Use quickstart.md scenarios**:
- Create task with various phrasings
- List tasks with filters
- Complete/update/delete tasks
- Handle errors and edge cases

## Dependencies

### Required Packages

```python
# requirements.txt additions
openai-agents>=1.0.0  # OpenAI Agent SDK
openai>=1.0.0         # OpenAI Python SDK (for model interface)
```

### Existing Dependencies (Reused)

- FastAPI (API framework)
- Pydantic (validation)
- MCP Python SDK (tool integration)
- SQLModel (via MCP tools)

## Deployment Considerations

### Environment Variables

```bash
GEMINI_API_KEY=<api-key>  # Gemini API key for model routing
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

### Configuration

```python
# config.py additions
class Settings(BaseSettings):
    gemini_api_key: str
    openai_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    agent_model: str = "gemini-1.5-flash"
    agent_timeout: int = 30  # seconds
```

## Open Questions

None - all technical decisions resolved based on user input and constitution requirements.
