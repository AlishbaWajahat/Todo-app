---
id: 0002
title: Create MCP Task Tools Implementation Plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-mcp-task-tools
branch: 004-mcp-task-tools
user: user
command: /sp.plan
labels: ["plan", "mcp", "task-tools", "phase-iii", "stateless-architecture", "backend", "pydantic-schemas"]
links:
  spec: specs/004-mcp-task-tools/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-mcp-task-tools/plan.md
  - specs/004-mcp-task-tools/research.md
  - specs/004-mcp-task-tools/data-model.md
  - specs/004-mcp-task-tools/quickstart.md
  - specs/004-mcp-task-tools/contracts/list_tasks.json
  - specs/004-mcp-task-tools/contracts/add_task.json
  - specs/004-mcp-task-tools/contracts/complete_task.json
  - specs/004-mcp-task-tools/contracts/update_task.json
  - specs/004-mcp-task-tools/contracts/delete_task.json
  - CLAUDE.md
tests:
  - none
---

## Prompt

Before making plan review my frontend and backend folder to understand exsiting code structure and then plan accordingly Objective:
Implement a stateless MCP server exposing task operations as AI-callable tools.

Steps:
1. Initialize MCP server using Official MCP SDK
2. Define MCP tools:
   - add_task
   - list_tasks
   - update_task
   - complete_task
   - delete_task
3. For each tool:
   - Define explicit input/output schema
   - Validate user_id and task ownership
   - Persist all changes via SQLModel
4. Ensure no in-memory state or caching
5. Keep MCP layer isolated from agent and chat logic

Validation:
- Each tool performs correct DB operation
- Tools are stateless and restart-safe
- Cross-user access is impossible
- Input/output schemas are enforced
- No unused files or scaffolding remain

Notes:
- Do not add agent logic or NLP
- Assume auth is already validated upstream
- Clean file structure after implementation

## Response snapshot

Created comprehensive implementation plan for MCP Server & Task Tools feature (004-mcp-task-tools).

**Planning Approach**:
1. Reviewed existing backend structure (FastAPI, SQLModel, Task model, database patterns)
2. Reviewed constitution requirements (Principles VII, VIII, IX for stateless MCP architecture)
3. Completed Phase 0 research on Official MCP SDK patterns
4. Completed Phase 1 design with data models, contracts, and testing guide

**Implementation Plan Structure**:
- **Summary**: Stateless MCP server with 5 tools, integrated into existing FastAPI backend
- **Technical Context**: Python 3.11+, Official MCP SDK, FastAPI, SQLModel, Neon PostgreSQL
- **Constitution Check**: ✅ PASSED all requirements (stateless, MCP standards, security)
- **Project Structure**: New `backend/mcp/` module with schemas and tools subdirectories
- **Phase 0 Research**: 5 research areas documented (SDK patterns, tool definition, integration, error handling, stateless design)
- **Phase 1 Design**: Data model, 5 JSON contracts, quickstart testing guide

**Key Architectural Decisions**:
1. **MCP Server Integration**: Separate process (stdio) sharing database engine with FastAPI
2. **Tool Schemas**: Explicit Pydantic models for all inputs (user_id required) and outputs (ToolResponse with success/data/error/error_code)
3. **Error Handling**: Structured error codes (INVALID_USER_ID, TASK_NOT_FOUND, VALIDATION_ERROR, DATABASE_ERROR, INTERNAL_ERROR)
4. **Security**: Return TASK_NOT_FOUND (not permission denied) to prevent information leakage
5. **Stateless Design**: Pure functions, no caching, database is single source of truth

**Design Artifacts Created**:
- `research.md`: MCP SDK patterns, tool definition, integration, error handling, stateless design
- `data-model.md`: ToolResponse schema, 5 input schemas, output formats, query patterns, validation rules
- `contracts/`: 5 JSON schemas (list_tasks, add_task, complete_task, update_task, delete_task)
- `quickstart.md`: Testing guide with MCP Inspector, test scenarios, user isolation tests, stateless verification, performance benchmarks

**Constitution Compliance**:
- ✅ Principle VII (Stateless Architecture): No in-memory state, DB-backed, restart-safe
- ✅ Principle VIII (MCP Tool Standards): Explicit schemas, user_id enforcement, structured responses
- ✅ Principle IX (Agent-Tool Interaction): Tools provide abstraction, no direct DB access
- ✅ Security-First: user_id validation on all operations
- ✅ Technology Stack: Python, FastAPI, SQLModel, Official MCP SDK

**Module Structure**:
```
backend/mcp/
├── server.py              # MCP server initialization
├── schemas/
│   ├── base.py           # ToolResponse
│   ├── task_inputs.py    # 5 input schemas
│   └── task_outputs.py   # Output schemas
└── tools/
    ├── list_tasks.py
    ├── add_task.py
    ├── complete_task.py
    ├── update_task.py
    └── delete_task.py
```

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation - defines stateless MCP architecture with 5 tools, explicit schemas, and comprehensive testing strategy
- 🧪 Tests: Planning phase complete - testing guide created in quickstart.md with user isolation, stateless verification, and performance benchmarks
- 📁 Files: Created plan.md, research.md, data-model.md, quickstart.md, 5 contract JSON files; updated CLAUDE.md with new technology
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks, then `/sp.implement` to execute with Backend Agent
- 🧠 Reflection: Plan successfully balances technical precision (MCP protocol, Pydantic schemas, stateless architecture) with practical implementation (reuse existing infrastructure, share database engine, clear module structure). All constitution requirements satisfied. Ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all artifacts generated
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all Principles VII, VIII, IX satisfied)
- Prompt variant (if applicable): plan-mcp-tools-v1
- Next experiment (smallest change to try): Validate Official MCP SDK compatibility during implementation to ensure all tool patterns are supported
