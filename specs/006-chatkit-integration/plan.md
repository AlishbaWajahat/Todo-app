# Implementation Plan: ChatKit UI & End-to-End Integration

**Branch**: `006-chatkit-integration` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-chatkit-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate OpenAI ChatKit UI component into the existing Next.js frontend and connect it end-to-end with the FastAPI backend agent. Add database-backed conversation persistence to support stateless architecture. Users will manage tasks entirely through natural language chat commands, with conversations surviving server restarts and browser sessions.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x with Next.js 16.0.10, React 19.2.0
- Backend: Python 3.11+ with FastAPI

**Primary Dependencies**:
- Frontend: @openai/chatkit-react 1.4.3 (already installed), Better Auth 1.4.18, Tailwind CSS 4
- Backend: FastAPI, SQLModel, openai-agents 0.8.0, mcp 1.0.0, Gemini API (via OpenAI-compatible endpoint)
- Note: Backend currently uses Gemini (not Anthropic Claude) via OpenAI SDK routing

**Storage**: Neon Serverless PostgreSQL
- Existing tables: users, tasks
- New tables needed: conversations, messages, tool_calls
- Schema design: UUID for conversation_id, BIGSERIAL for messages, JSONB for tool metadata

**Testing**: Out of scope for Phase III (per constitution)

**Target Platform**: Web application (modern browsers with JavaScript enabled)

**Project Type**: Web (frontend + backend with AI agent integration)

**Performance Goals**:
- Agent response time: <5 seconds for 95% of requests
- Chat UI load time: <2 seconds on standard broadband
- Message history: Load last 50 messages initially, paginate older messages

**Constraints**:
- Stateless architecture (NON-NEGOTIABLE): No in-memory state, all conversation data in database
- Server restart resilience: Conversations must survive backend restarts
- User isolation: JWT-based authentication, strict user_id filtering
- Preserve existing theme/layout: ChatKit must integrate into existing (protected) layout
- Existing agent endpoint: Must work with current `/api/v1/agent/chat` or create new endpoint

**Scale/Scope**:
- Single-user chat sessions (no multi-user conversations)
- Conversation persistence across browser sessions and server restarts
- Support for all 5 basic task operations via natural language
- End-to-end flow: ChatKit UI → FastAPI → Agent → MCP Tools → Database → Response

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Stateless Architecture (NON-NEGOTIABLE - Principle VII)
- ✅ PASS: No in-memory chat history planned (database-backed)
- ✅ PASS: No in-memory tool state planned (existing MCP tools are stateless)
- ✅ PASS: Conversation history will be rebuilt from database on every request
- ✅ PASS: Server restart will NOT break conversations (database persistence)
- ✅ PASS: All chat messages will be persisted before response
- ✅ PASS: Database is single source of truth for conversation state

**Status**: PASS - Design adheres to stateless architecture requirements

### Gate 2: MCP Tool Standards (NON-NEGOTIABLE - Principle VIII)
- ✅ PASS: Existing MCP tools are stateless (verified in backend/mcp/tools/)
- ✅ PASS: Existing tools query database for all data (no caching)
- ✅ PASS: Existing tools have explicit Pydantic input schemas with user_id
- ✅ PASS: Existing tools have explicit Pydantic output schemas with success field
- ✅ PASS: Existing tools enforce user_id ownership (filter by authenticated user)
- ✅ PASS: Existing tools validate all inputs before execution
- ✅ PASS: Existing tools return structured JSON responses

**Status**: PASS - Existing MCP tools already meet all standards

### Gate 3: Agent-Tool Interaction Rules (Principle IX)
- ✅ PASS: Existing agent uses MCP tools for all task operations (verified in backend/agent/agent.py)
- ✅ PASS: Existing agent does NOT access database directly
- ⚠️ NEEDS IMPLEMENTATION: Agent does not currently request confirmation for destructive actions
- ✅ PASS: Agent validates tool responses before presenting to user
- ✅ PASS: Agent passes authenticated user_id to all tool calls

**Status**: CONDITIONAL PASS - Need to add confirmation prompts for destructive actions (delete, bulk operations)

### Gate 4: Security-First Architecture (Principle III - Phase III)
- ✅ PASS: Chat endpoint will require valid JWT authentication
- ✅ PASS: All MCP tool calls will include user_id from authenticated JWT
- ✅ PASS: Conversation history will be filtered by authenticated user_id
- ✅ PASS: Tool calls will validate user_id matches authenticated user
- ✅ PASS: No cross-user conversation access

**Status**: PASS - Design adheres to Phase III security requirements

### Gate 5: Technology Stack Adherence (Principle IV - AI Chatbot Stack)
- ⚠️ DEVIATION: Using Gemini (via OpenAI SDK) instead of Anthropic Claude SDK
- ✅ PASS: Using Model Context Protocol (MCP) for tool integration
- ✅ PASS: Using OpenAI ChatKit for frontend UI (already installed)
- ✅ PASS: Using Pydantic models for tool schemas
- ✅ PASS: Using Neon PostgreSQL for conversation storage

**Status**: CONDITIONAL PASS - Constitution specifies Anthropic Claude, but existing implementation uses Gemini. This is a documented deviation that must be acknowledged.

### Overall Constitution Compliance: ⚠️ CONDITIONAL PASS

**Deviations Requiring Justification:**
1. **AI Model**: Using Gemini instead of Anthropic Claude (existing implementation)
2. **Confirmation Prompts**: Need to add for destructive actions

**Justification**: The existing agent implementation uses Gemini via OpenAI-compatible API. Switching to Anthropic Claude would require significant refactoring of the agent module. For Phase III MVP, we will maintain Gemini and document this as a known deviation. Future phases can migrate to Claude if needed.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── agent/
│   ├── agent.py                 # EXISTING: Stateless agent with MCP tool invocation
│   ├── intent_parser.py         # EXISTING: Natural language intent classification
│   └── response_formatter.py    # EXISTING: Format tool responses as natural language
├── api/
│   └── v1/
│       └── endpoints/
│           ├── agent.py         # EXISTING: POST /api/v1/agent/chat endpoint
│           ├── auth.py          # EXISTING: Authentication endpoints
│           ├── tasks.py         # EXISTING: Task CRUD endpoints
│           └── users.py         # EXISTING: User management endpoints
├── mcp/
│   ├── server.py                # EXISTING: MCP server with 5 registered tools
│   ├── tools/
│   │   ├── list_tasks.py        # EXISTING: List user's tasks
│   │   ├── add_task.py          # EXISTING: Create new task
│   │   ├── complete_task.py     # EXISTING: Mark task complete/incomplete
│   │   ├── update_task.py       # EXISTING: Update task details
│   │   └── delete_task.py       # EXISTING: Delete task
│   └── schemas/
│       ├── base.py              # EXISTING: Base response schema
│       └── task_inputs.py       # EXISTING: Pydantic input schemas for all tools
├── models/
│   ├── user.py                  # EXISTING: User SQLModel
│   ├── task.py                  # EXISTING: Task SQLModel
│   ├── conversation.py          # NEW: Conversation model for chat history
│   ├── message.py               # NEW: Message model for chat messages
│   └── tool_call.py             # NEW: Tool call execution record
├── core/
│   ├── config.py                # EXISTING: Settings with JWT, database, Gemini API
│   ├── database.py              # EXISTING: Database session management
│   └── security.py              # EXISTING: JWT verification utilities
├── dependencies/
│   └── auth.py                  # EXISTING: JWT authentication dependency
├── middleware/
│   └── auth.py                  # EXISTING: Authentication middleware
└── alembic/
    └── versions/                # EXISTING: Database migrations
        └── [new]_add_conversation_tables.py  # NEW: Migration for chat tables

frontend/
├── app/
│   ├── (auth)/
│   │   ├── signin/              # EXISTING: Sign-in page
│   │   └── signup/              # EXISTING: Sign-up page
│   ├── (protected)/
│   │   ├── layout.tsx           # EXISTING: Protected routes layout with auth
│   │   ├── dashboard/           # EXISTING: Dashboard page
│   │   ├── profile/             # EXISTING: User profile page
│   │   ├── tasks/               # EXISTING: Task management pages
│   │   │   ├── new/             # EXISTING: Create task page
│   │   │   └── [id]/edit/       # EXISTING: Edit task page
│   │   └── chat/                # EXISTING DIRECTORY (empty or minimal)
│   │       ├── page.tsx         # NEW/UPDATE: Chat page with ChatKit integration
│   │       └── layout.tsx       # NEW: Chat-specific layout (optional)
│   ├── layout.tsx               # EXISTING: Root layout
│   └── page.tsx                 # EXISTING: Landing page
├── components/
│   ├── auth/                    # EXISTING: Auth components
│   ├── layout/
│   │   └── Header.tsx           # EXISTING: Navigation header
│   ├── tasks/                   # EXISTING: Task components
│   ├── ui/                      # EXISTING: Reusable UI components
│   └── chat/                    # NEW: Chat-specific components
│       ├── ChatKitWrapper.tsx   # NEW: ChatKit component wrapper
│       ├── ChatInterface.tsx    # NEW: Main chat interface
│       └── ConversationList.tsx # NEW: Conversation history sidebar (optional)
└── lib/
    ├── api/
    │   ├── client.ts            # EXISTING: Base API client with auth
    │   ├── auth.ts              # EXISTING: Auth API calls
    │   ├── tasks.ts             # EXISTING: Task API calls
    │   └── chat.ts              # NEW: Chat API calls
    ├── auth/
    │   ├── config.ts            # EXISTING: Better Auth configuration
    │   └── index.ts             # EXISTING: Auth utilities
    ├── hooks/
    │   ├── useAuth.ts           # EXISTING: Auth hook
    │   └── useChat.ts           # NEW: Chat state management hook
    └── types/
        ├── task.ts              # EXISTING: Task types
        ├── user.ts              # EXISTING: User types
        └── chat.ts              # NEW: Chat/conversation types

database/ (Neon PostgreSQL)
├── users                        # EXISTING: User accounts
├── tasks                        # EXISTING: Task items
├── conversations                # NEW: Chat conversations
├── messages                     # NEW: Chat messages
└── tool_calls                   # NEW: Tool execution records
```

**Structure Decision**: Web application structure with separate backend and frontend directories. This feature adds conversation persistence to the existing agent architecture. The frontend already has a `/chat` route directory under `(protected)`, which will be populated with ChatKit integration. The backend agent and MCP tools are already functional and stateless, requiring only conversation storage and endpoint modifications.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Using Gemini instead of Anthropic Claude (Principle IV) | Existing agent implementation is built on Gemini via OpenAI SDK. Backend uses `openai-agents` package with Gemini routing. | Switching to Anthropic Claude would require: (1) Rewriting agent.py to use Anthropic SDK, (2) Changing tool invocation patterns, (3) Modifying response streaming, (4) Testing entire agent flow. This is out of scope for Phase III MVP. Gemini provides equivalent functionality for task management use case. |
| Missing confirmation prompts for destructive actions (Principle IX) | Current agent implementation does not prompt for confirmation before delete operations. | Will be added as part of this feature implementation. Agent will detect destructive intents (delete, bulk operations) and request user confirmation before executing MCP tools. |

**Mitigation Plan**:
1. **Gemini Deviation**: Document as known limitation. Add ADR explaining decision. Plan future migration to Claude in Phase IV if needed.
2. **Confirmation Prompts**: Implement in agent response flow. Add confirmation state to conversation context. User must explicitly confirm destructive actions.

---

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 design completion*

### Gate 1: Stateless Architecture ✅ PASS
- Database schema designed with proper persistence (conversations, messages, tool_calls)
- No in-memory state in design
- Conversation history loaded from database on every request
- Server restart resilience confirmed through database-backed design

### Gate 2: MCP Tool Standards ✅ PASS
- Existing MCP tools meet all requirements (verified in backend/mcp/)
- No changes needed to tool implementations
- Tools remain stateless and database-backed

### Gate 3: Agent-Tool Interaction Rules ⚠️ NEEDS IMPLEMENTATION
- Confirmation prompts designed in research.md
- Two-step confirmation flow specified
- Implementation required in agent.py

### Gate 4: Security-First Architecture ✅ PASS
- JWT authentication enforced in API contract
- User isolation enforced through database schema (user_id foreign keys)
- Conversation ownership validated in endpoint design
- No cross-user access possible

### Gate 5: Technology Stack Adherence ⚠️ DOCUMENTED DEVIATION
- Gemini usage documented and justified in Complexity Tracking
- All other stack requirements met
- ChatKit integration follows best practices

### Overall Post-Design Compliance: ✅ PASS WITH NOTED DEVIATIONS

**Action Items for Implementation**:
1. Add confirmation prompt logic to agent.py (Principle IX compliance)
2. Document Gemini usage in ADR (Principle IV deviation)

---

## Phase 0 & Phase 1 Completion Summary

**Phase 0: Research** ✅ COMPLETE
- Created: `research.md`
- Resolved: ChatKit integration, database schema, endpoint design, session management, confirmation prompts, pagination
- All NEEDS CLARIFICATION items resolved

**Phase 1: Design & Contracts** ✅ COMPLETE
- Created: `data-model.md` (3 SQLModel entities with relationships)
- Created: `contracts/chat-api.json` (OpenAPI 3.1 specification)
- Created: `quickstart.md` (setup and testing guide)
- Updated: `CLAUDE.md` (agent context with new technologies)

**Artifacts Generated**:
1. `specs/006-chatkit-integration/plan.md` (this file)
2. `specs/006-chatkit-integration/research.md`
3. `specs/006-chatkit-integration/data-model.md`
4. `specs/006-chatkit-integration/quickstart.md`
5. `specs/006-chatkit-integration/contracts/chat-api.json`

**Ready for**: Phase 2 - Task Generation (`/sp.tasks` command)

---

## Implementation Readiness Checklist

- [x] All research questions answered
- [x] Database schema designed with SQLModel
- [x] API contracts defined with OpenAPI
- [x] Setup instructions documented
- [x] Constitution compliance verified
- [x] Deviations documented and justified
- [x] Agent context updated
- [x] Existing codebase structure analyzed
- [x] Integration points identified
- [x] Security requirements addressed

**Status**: ✅ PLANNING COMPLETE - Ready for task breakdown via `/sp.tasks`
