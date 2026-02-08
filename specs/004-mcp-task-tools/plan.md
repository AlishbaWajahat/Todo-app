# Implementation Plan: MCP Server & Task Tools for AI Todo Chatbot

**Branch**: `004-mcp-task-tools` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-mcp-task-tools/spec.md`

## Summary

Implement a stateless MCP (Model Context Protocol) server that exposes task management operations as AI-callable tools. The MCP server will integrate into the existing FastAPI backend and provide 5 tools (list_tasks, add_task, complete_task, update_task, delete_task) that enable AI agents to manage user tasks through structured, validated function calls. All tools enforce strict user isolation, persist data to PostgreSQL via SQLModel, and maintain zero in-memory state for server restart resilience.

**Technical Approach**: Create a new `backend/mcp/` module containing the MCP server initialization, tool implementations, and Pydantic schemas. Tools will reuse existing database infrastructure (SQLModel, connection pooling) and Task model while adding MCP-specific input/output validation. The MCP server will run alongside the FastAPI application, sharing the same database connection pool.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- Official MCP SDK for Python (mcp package)
- FastAPI 0.104+ (existing)
- SQLModel 0.0.14+ (existing)
- Pydantic 2.5+ (existing, included with SQLModel)
- psycopg2-binary 2.9+ (existing, for PostgreSQL)

**Storage**: Neon Serverless PostgreSQL (existing database, reuse tasks table)
**Testing**: pytest (existing test infrastructure)
**Target Platform**: Linux server / Docker container (same as existing FastAPI backend)
**Project Type**: Web application (backend extension)

**Performance Goals**:
- MCP server initialization: <2 seconds
- Tool call latency: <500ms for list_tasks (up to 100 tasks)
- Tool call latency: <1 second for write operations (add, update, complete, delete)
- Database query performance: <100ms for typical workloads (up to 50 tasks per user)

**Constraints**:
- Must use Official MCP SDK only (no custom implementations)
- Must be stateless (no in-memory caching or session storage)
- Must enforce user_id ownership on every database query
- Must use existing Task model (no schema duplication)
- Must integrate with existing FastAPI backend (not a separate service)
- Must follow Constitution Principle VIII (MCP Tool Standards)

**Scale/Scope**:
- 5 MCP tools (CRUD operations for tasks)
- Support for concurrent AI agent calls (stateless design)
- Typical workload: 10-50 tasks per user, 100-1000 users
- No pagination required for MVP (list_tasks returns all user tasks)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle VII: Stateless Architecture (NON-NEGOTIABLE)
- ✅ **PASS**: All tools will be stateless functions with no class-level or global state
- ✅ **PASS**: All data persisted to PostgreSQL before returning success
- ✅ **PASS**: Conversation history not applicable (MCP tools don't maintain conversation state)
- ✅ **PASS**: Server restart resilience guaranteed by database-backed design

### Principle VIII: MCP Tool Standards (NON-NEGOTIABLE)
- ✅ **PASS**: All tools will have explicit Pydantic input schemas (e.g., AddTaskInput, ListTasksInput)
- ✅ **PASS**: All tools will have explicit Pydantic output schemas (ToolResponse with success, data, error, error_code)
- ✅ **PASS**: All tools will include user_id in input schema and enforce ownership
- ✅ **PASS**: All tools will filter database queries by user_id
- ✅ **PASS**: All tools will return structured JSON responses (not plain text)

### Principle IX: Agent-Tool Interaction Rules
- ✅ **PASS**: Tools provide abstraction layer - AI agent cannot access database directly
- ✅ **PASS**: Tools validate all inputs via Pydantic before database operations
- ⚠️ **PARTIAL**: Action confirmations not applicable at tool level (handled by AI agent layer)
- ✅ **PASS**: Tools handle errors gracefully with user-friendly messages and error codes

### Additional Constitution Requirements
- ✅ **PASS**: Spec-Driven Development - This plan follows approved spec
- ✅ **PASS**: Zero Manual Coding - Implementation will use Claude Code agents
- ✅ **PASS**: Security-First - user_id validation and ownership enforcement on all operations
- ✅ **PASS**: Technology Stack Adherence - Python, FastAPI, SQLModel, Official MCP SDK
- ✅ **PASS**: Secrets Management - No hardcoded credentials (DATABASE_URL from environment)

**Gate Result**: ✅ **PASSED** - All constitution requirements satisfied. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/004-mcp-task-tools/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already created)
├── research.md          # Phase 0 output (MCP SDK patterns, best practices)
├── data-model.md        # Phase 1 output (Tool schemas, response formats)
├── quickstart.md        # Phase 1 output (How to test MCP tools)
├── contracts/           # Phase 1 output (Tool input/output schemas)
│   ├── add_task.json
│   ├── list_tasks.json
│   ├── update_task.json
│   ├── complete_task.json
│   └── delete_task.json
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── mcp/                          # NEW: MCP server module
│   ├── __init__.py              # Module initialization
│   ├── server.py                # MCP server initialization and registration
│   ├── schemas/                 # NEW: MCP-specific Pydantic schemas
│   │   ├── __init__.py
│   │   ├── base.py             # ToolResponse base schema
│   │   ├── task_inputs.py      # Input schemas for all tools
│   │   └── task_outputs.py     # Output schemas for all tools
│   └── tools/                   # NEW: MCP tool implementations
│       ├── __init__.py
│       ├── list_tasks.py       # list_tasks tool
│       ├── add_task.py         # add_task tool
│       ├── complete_task.py    # complete_task tool
│       ├── update_task.py      # update_task tool
│       └── delete_task.py      # delete_task tool
├── models/                       # EXISTING: Database models
│   ├── task.py                  # REUSE: Existing Task model
│   └── user.py                  # REUSE: Existing User model
├── core/                         # EXISTING: Core infrastructure
│   ├── database.py              # REUSE: get_session(), engine
│   ├── config.py                # REUSE: settings
│   └── security.py              # REUSE: JWT utilities (if needed)
├── main.py                       # MODIFY: Register MCP server on startup
└── requirements.txt              # MODIFY: Add mcp package

frontend/                         # UNCHANGED: No frontend changes for this feature
└── [existing structure]
```

**Structure Decision**: Web application (backend extension). The MCP server will be implemented as a new module (`backend/mcp/`) within the existing FastAPI backend. This approach:
- Reuses existing database infrastructure (connection pooling, SQLModel)
- Shares the same Task model (no duplication)
- Runs in the same process as FastAPI (simplified deployment)
- Maintains separation of concerns (MCP tools isolated from REST API)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitution requirements satisfied.

---

## Phase 0: Research & Discovery

### Research Tasks

1. **Official MCP SDK for Python**
   - **Question**: How to initialize an MCP server using the Official MCP SDK?
   - **Research Goal**: Find SDK documentation, initialization patterns, tool registration API
   - **Output**: Code examples for server setup and tool registration

2. **MCP Tool Definition Patterns**
   - **Question**: How to define MCP tools with explicit input/output schemas?
   - **Research Goal**: Understand MCP tool decorator/registration patterns, schema validation
   - **Output**: Best practices for tool implementation with Pydantic

3. **MCP Server Integration with FastAPI**
   - **Question**: How to run MCP server alongside FastAPI application?
   - **Research Goal**: Lifecycle management, shared resources (database connections)
   - **Output**: Integration pattern for FastAPI lifespan events

4. **Error Handling in MCP Tools**
   - **Question**: What's the standard error response format for MCP tools?
   - **Research Goal**: Error codes, error messages, exception handling patterns
   - **Output**: Error handling best practices and response schema

5. **Stateless Tool Design**
   - **Question**: How to ensure MCP tools are truly stateless?
   - **Research Goal**: Common pitfalls (global variables, class state), validation techniques
   - **Output**: Checklist for stateless tool implementation

### Research Execution

**Status**: ✅ **COMPLETED**

Research findings documented in `research.md` covering:
1. Official MCP SDK for Python - initialization patterns and tool registration
2. MCP Tool Definition with Pydantic schemas - input/output validation
3. MCP Server Integration with FastAPI - shared database, separate process
4. Error Handling in MCP Tools - structured responses with error codes
5. Stateless Tool Design - pure functions, no shared state

**Key Decisions**:
- Use Official MCP SDK (`mcp` package) for protocol compliance
- Run MCP server as separate process (stdio communication)
- Share database engine between FastAPI and MCP server
- Use Pydantic models for all tool input/output validation
- Return structured ToolResponse with success, data, error, error_code

---

## Phase 1: Design & Contracts

### Design Artifacts

**Status**: ✅ **COMPLETED**

#### 1. Data Model (`data-model.md`)

Comprehensive data model documentation including:
- **Core Entities**: Task (existing SQLModel, reused)
- **Base Response Schema**: ToolResponse with success, data, error, error_code
- **Tool Input Schemas**: 5 Pydantic models (ListTasksInput, AddTaskInput, CompleteTaskInput, UpdateTaskInput, DeleteTaskInput)
- **Tool Output Data Structures**: Standard formats for each tool's response
- **Database Query Patterns**: User isolation and ownership verification
- **State Management**: Stateless design principles and session management
- **Validation Summary**: Input/output validation checklists

**Key Design Decisions**:
- Reuse existing Task model (no duplication)
- Enforce user_id in all input schemas
- Use consistent error code taxonomy (INVALID_USER_ID, TASK_NOT_FOUND, VALIDATION_ERROR, DATABASE_ERROR, INTERNAL_ERROR)
- Return TASK_NOT_FOUND (not permission denied) for security
- Title max 500 chars, description max 2000 chars

#### 2. API Contracts (`contracts/`)

Generated JSON schemas for all 5 MCP tools:
- ✅ `list_tasks.json` - Retrieve tasks with optional filtering
- ✅ `add_task.json` - Create new task
- ✅ `complete_task.json` - Toggle completion status
- ✅ `update_task.json` - Update title/description
- ✅ `delete_task.json` - Permanently delete task

Each contract includes:
- Input schema with validation rules
- Output schema with success/error structure
- Example requests and responses
- Error code enumerations

#### 3. Quickstart Guide (`quickstart.md`)

Testing documentation covering:
- Prerequisites and setup
- Running the MCP server
- Testing tools with MCP Inspector and Python scripts
- Test scenarios for all 5 tools
- User isolation testing (security verification)
- Stateless verification testing (server restart resilience)
- Performance testing (latency benchmarks)
- Troubleshooting guide

#### 4. Agent Context Update

Updated `CLAUDE.md` with:
- Python 3.11+ as active technology
- Neon Serverless PostgreSQL (existing database)
- MCP server integration context

### Constitution Re-Check

**Status**: ✅ **PASSED** (no changes from initial check)

All Phase 1 design artifacts comply with constitution requirements:
- ✅ Stateless Architecture (Principle VII)
- ✅ MCP Tool Standards (Principle VIII)
- ✅ Agent-Tool Interaction Rules (Principle IX)
- ✅ Security-First Architecture (user_id enforcement)
- ✅ Technology Stack Adherence (Python, FastAPI, SQLModel, Official MCP SDK)

---

## Phase 2: Task Generation

**Status**: ⏸️ **PENDING** - Use `/sp.tasks` command to generate implementation tasks

The planning phase is complete. Next steps:

1. **Generate Tasks**: Run `/sp.tasks` to break down the implementation into atomic, testable tasks
2. **Implementation**: Use Backend Agent with Backend Skill to implement MCP tools
3. **Testing**: Follow quickstart.md to verify all tools work correctly
4. **Security Audit**: Verify user isolation and stateless architecture

---

## Summary

### What Was Planned

**MCP Server & Task Tools** - A stateless Model Context Protocol server that exposes 5 task management tools (list_tasks, add_task, complete_task, update_task, delete_task) for AI agent consumption.

**Architecture**:
- New `backend/mcp/` module with server, schemas, and tool implementations
- Reuses existing Task model and database infrastructure
- Runs as separate process alongside FastAPI
- Shares database connection pool for efficiency
- Enforces strict user isolation on all operations
- Maintains zero in-memory state for restart resilience

**Key Technical Decisions**:
1. **MCP SDK**: Use Official MCP SDK for protocol compliance
2. **Integration**: Separate process (stdio) sharing database engine
3. **Schemas**: Explicit Pydantic models for all inputs/outputs
4. **Error Handling**: Structured responses with error codes
5. **Security**: user_id validation and ownership enforcement on every query
6. **Stateless**: Pure functions, database-backed, no caching

### Artifacts Generated

- ✅ `plan.md` - This implementation plan
- ✅ `research.md` - MCP SDK research and best practices
- ✅ `data-model.md` - Detailed schemas and data structures
- ✅ `contracts/` - 5 JSON schema contracts for tools
- ✅ `quickstart.md` - Testing and verification guide
- ✅ Agent context updated with new technology

### Ready for Implementation

All design artifacts are complete and validated. The feature is ready for task generation (`/sp.tasks`) and implementation.

**Estimated Complexity**: Medium
- 5 tools to implement (similar patterns)
- Reuses existing infrastructure (database, models)
- Clear contracts and schemas defined
- Comprehensive testing guide available

**Implementation Order** (recommended):
1. Create MCP module structure (`backend/mcp/`)
2. Implement base schemas (`ToolResponse`, input models)
3. Implement list_tasks (read-only, simplest)
4. Implement add_task (write operation)
5. Implement complete_task (update operation)
6. Implement update_task (partial update)
7. Implement delete_task (delete operation)
8. Test all tools with quickstart guide
9. Verify user isolation and stateless architecture

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| MCP SDK API changes | Low | High | Pin mcp version in requirements.txt |
| Database connection pool exhaustion | Medium | Medium | Share engine between FastAPI and MCP server |
| User isolation bypass | Low | Critical | Comprehensive security testing, code review |
| Performance degradation | Low | Medium | Database query optimization, indexing |
| Stateless verification failure | Low | High | Automated restart testing in CI/CD |

---

## Next Steps

1. **Run `/sp.tasks`** to generate implementation tasks from this plan
2. **Review tasks** for completeness and ordering
3. **Run `/sp.implement`** to execute tasks using Backend Agent
4. **Test thoroughly** using quickstart.md guide
5. **Security audit** to verify user isolation
6. **Performance testing** to validate latency requirements

**Planning Phase Complete** ✅
