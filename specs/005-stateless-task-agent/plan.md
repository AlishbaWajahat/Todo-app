# Implementation Plan: Stateless Task Agent with MCP Tool Invocation

**Branch**: `005-stateless-task-agent` | **Date**: 2026-02-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-stateless-task-agent/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a stateless AI agent that interprets natural language user messages and invokes MCP task management tools (create, list, update, complete, delete). The agent uses OpenAI Agent SDK with Gemini-backed model routing, maintains zero state between requests, and translates tool outputs into concise natural language responses. All task operations occur exclusively through MCP tools with strict user isolation.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- OpenAI Agent SDK (openai-agents package)
- OpenAI Python SDK (for OpenAIChatCompletionModel)
- MCP Python SDK (mcp package) - for tool integration
- FastAPI (for API endpoint exposure)
- Pydantic (for request/response validation)

**Storage**: N/A (agent is stateless, all data operations via MCP tools)
**Testing**: pytest with test fixtures for MCP tool mocking
**Target Platform**: Linux server (containerized deployment)
**Project Type**: Web application (backend-only component)
**Performance Goals**:
- <2 seconds response time (95th percentile)
- Support 100+ concurrent requests
- 95% intent classification accuracy

**Constraints**:
- Stateless per request (no session state, no conversation history)
- No direct database access (MCP tools only)
- No embeddings or vector databases
- Minimal file count (1-3 files for agent logic)
- Gemini API routing via OpenAI-compatible interface

**Scale/Scope**:
- Single agent endpoint
- 5 MCP tool integrations
- Support for 1000+ users
- Deterministic, rule-based intent mapping

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle VII: Stateless Architecture ✅ PASS
- Agent maintains zero state between requests
- No conversation history storage
- No in-memory caching
- All data operations via MCP tools (database-backed)

### Principle VIII: MCP Tool Standards ✅ PASS
- Agent uses existing MCP tools from 004-mcp-task-tools
- All tool calls include user_id for isolation
- No direct database access from agent layer

### Principle IX: Agent-Tool Interaction Rules ✅ PASS
- Agent invokes MCP tools exclusively (no direct DB access)
- User confirmations handled via natural language responses
- Tool outputs translated to user-friendly messages

### Code Quality Standards ✅ PASS
- Minimal file structure (agent logic in 1-3 files)
- Modular design (intent parsing, tool invocation, response generation)
- No unused files after completion

## Project Structure

### Documentation (this feature)

```text
specs/005-stateless-task-agent/
├── spec.md              # Feature specification
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── agent_endpoint.json  # API contract for agent endpoint
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── agent/                      # NEW: Stateless task agent module
│   ├── __init__.py
│   ├── agent.py               # Agent initialization and request handling
│   ├── intent_parser.py       # Intent classification and parameter extraction
│   └── response_formatter.py  # Tool output → natural language conversion
├── mcp/                       # EXISTING: MCP tools (004-mcp-task-tools)
│   ├── server.py
│   ├── schemas/
│   └── tools/
├── api/                       # EXISTING: FastAPI routes
│   └── agent_routes.py        # NEW: Agent endpoint
├── models/                    # EXISTING: Database models
├── core/                      # EXISTING: Config, database
└── tests/
    └── agent/                 # NEW: Agent tests
        ├── test_intent_parser.py
        ├── test_agent.py
        └── test_response_formatter.py
```

**Structure Decision**: Web application structure (backend-only). Agent module added to existing backend/ directory alongside MCP tools. Minimal file count (3 files for agent logic) with clear separation of concerns: intent parsing, tool invocation, response formatting.
