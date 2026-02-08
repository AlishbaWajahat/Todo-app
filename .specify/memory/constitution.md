<!--
Sync Impact Report - Constitution v1.2.0
========================================
Version Change: 1.1.0 → 1.2.0
Rationale: MINOR version bump - Added Phase III (AI-powered Todo Chatbot) principles and MCP architecture standards

Modified Principles:
- Principle III (Security-First Architecture): Added chatbot security requirements (JWT for chat/tool calls)
- Principle IV (Technology Stack Adherence): Added Claude SDK, MCP, and chatbot stack

Added Principles:
- Principle VII: Stateless Architecture (NON-NEGOTIABLE) - No in-memory state, DB-backed persistence
- Principle VIII: MCP Tool Standards (NON-NEGOTIABLE) - Stateless tools, explicit schemas, user_id enforcement
- Principle IX: Agent-Tool Interaction Rules - Agent must use MCP tools, no direct DB access, confirmations required

Added Sections:
- Phase III Compliance Checks (chatbot-specific verification)
  - Stateless Architecture Verification
  - MCP Tool Verification
  - Agent-Tool Interaction Verification
  - Conversation Persistence Verification
- Updated Definition of Done with Phase III criteria
- Updated Technology Stack with chatbot components

Removed Sections: None

Templates Requiring Updates:
- ✅ .specify/templates/plan-template.md (constitution check section compatible)
- ✅ .specify/templates/spec-template.md (acceptance criteria align with testable checks)
- ✅ .specify/templates/tasks-template.md (task verification aligns with compliance checks)
- ✅ .specify/templates/commands/*.md (no updates needed)

Follow-up TODOs: None

Key Improvements:
1. Added comprehensive stateless architecture requirements for chatbot
2. Added MCP tool standards with explicit input/output schema requirements
3. Added agent-tool interaction rules preventing direct DB access
4. Added conversation persistence requirements (server restart resilience)
5. Added Phase III security requirements (JWT for all chat/tool operations)
6. Added code hygiene standards (no unused files, modular structure)
7. All new rules are testable with PASS/FAIL criteria
-->

# Full-Stack Multi-User Todo Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All development MUST follow the explicit workflow: spec → plan → tasks → implementation.

**Testable Requirements:**
- Every feature begins with a written specification in `specs/<feature>/spec.md`
- Specifications MUST be approved before planning begins
- Plans MUST be derived from approved specs and documented in `specs/<feature>/plan.md`
- Tasks MUST be broken down from approved plans in `specs/<feature>/tasks.md`
- Implementation MUST follow the task list without deviation
- No code may be written without a corresponding spec, plan, and task

**Verification Checks:**
- ✅ PASS: For every code file, a corresponding task exists in `tasks.md`
- ✅ PASS: For every task, a corresponding plan section exists in `plan.md`
- ✅ PASS: For every plan, a corresponding spec exists in `spec.md`
- ✅ PASS: Git commits reference task IDs (e.g., "feat: implement task #3")
- ✅ PASS: PHR (Prompt History Record) exists for each implementation session
- ❌ FAIL: Code exists without traceable spec/plan/task lineage

**Rationale**: Deterministic, reproducible development requires explicit documentation
at every stage. This prevents scope creep, ensures traceability, and enables
AI-assisted development with clear context.

### II. Zero Manual Coding

All code MUST be generated via Claude Code using Spec-Kit Plus tooling.

**Testable Requirements:**
- No manual code writing is permitted
- All implementations MUST use Claude Code agents and skills
- Code generation MUST follow agent-specific guidelines (Frontend, Backend, Database, Auth)
- Manual edits are only permitted for emergency hotfixes (must be documented in ADR)
- All code changes MUST be traceable to a spec/plan/task

**Emergency Hotfix Criteria (Manual Edits Allowed):**
Manual edits are ONLY permitted when ALL of the following are true:
1. Production system is down or critically broken
2. Immediate fix required (cannot wait for spec-driven process)
3. Fix is < 10 lines of code
4. ADR documenting the hotfix is created within 24 hours
5. Proper spec/plan/task created retroactively within 48 hours

**Verification Checks:**
- ✅ PASS: All git commits authored by Claude Code or reference PHR
- ✅ PASS: All code changes have corresponding PHR in `history/prompts/`
- ✅ PASS: Manual edits (if any) have corresponding ADR in `history/adr/`
- ❌ FAIL: Git commits without PHR or ADR documentation

**Rationale**: Ensures consistency, leverages AI capabilities fully, and maintains
a clear audit trail of all development decisions and implementations.

### III. Security-First Architecture (NON-NEGOTIABLE)

Security MUST be the primary consideration in all architectural decisions.

**Phase II Requirements (Web Application):**
- All API routes MUST require valid JWT authentication
- JWT tokens MUST be verified on every backend request
- User data MUST be strictly isolated (users can only access their own data)
- Database queries MUST filter by authenticated user ID
- No hardcoded secrets or credentials anywhere in codebase
- All secrets MUST be managed via environment variables
- HTTPS MUST be enforced in production
- Authentication failures MUST return 401 Unauthorized
- Authorization failures MUST return 403 Forbidden

**Phase III Requirements (AI Chatbot):**
- All chat endpoints MUST require valid JWT authentication
- All MCP tool calls MUST include user_id from authenticated JWT
- Conversation history MUST be filtered by authenticated user_id
- Tool calls MUST validate user_id matches authenticated user
- Chat messages MUST be persisted with user_id for isolation
- No cross-user conversation access (strict isolation)
- Agent MUST NOT bypass authentication/authorization checks

**Rationale**: Multi-user applications require strict security boundaries. JWT-based
authentication with proper verification ensures user data isolation and prevents
unauthorized access. Chatbot security extends these principles to conversational AI,
ensuring users can only access their own conversations and todo data.

### IV. Technology Stack Adherence

All implementations MUST use the specified technology stack without deviation.

**Frontend (Phase II & III):**
- Next.js 16+ with App Router (no Pages Router)
- Tailwind CSS for styling (no other CSS frameworks)
- TypeScript for type safety

**Backend (Phase II & III):**
- Python FastAPI (no other Python frameworks)
- SQLModel for ORM (combines SQLAlchemy + Pydantic)
- Pydantic for request/response validation

**Database (Phase II & III):**
- Neon Serverless PostgreSQL (no other databases)
- Connection pooling configured for serverless
- Alembic for migrations

**Authentication (Phase II & III):**
- Better Auth for frontend authentication
- JWT tokens for backend verification
- python-jose for JWT handling in FastAPI

**AI Chatbot Stack (Phase III):**
- Anthropic Claude SDK (claude-3-5-sonnet or claude-3-5-haiku)
- Model Context Protocol (MCP) for tool integration
- Streaming responses for real-time chat experience
- Structured tool schemas (Pydantic models)

**Tooling:**
- Claude Code for all code generation
- Spec-Kit Plus for spec-driven workflow

**Rationale**: Technology constraints ensure consistency, enable agent specialization,
and prevent architectural drift. The chosen stack is optimized for serverless
deployment and AI-assisted development. MCP provides standardized tool integration
for AI agents.

### V. API Contract Discipline

Frontend and backend MUST communicate exclusively via well-defined REST APIs.

**Testable Requirements:**
- All API endpoints MUST follow RESTful conventions
- Request/response schemas MUST be defined with Pydantic/SQLModel
- API behavior MUST be consistent and predictable
- No direct database access from frontend
- No business logic in frontend (only presentation logic)
- API responses MUST use standard HTTP status codes
- Error responses MUST include meaningful error messages
- API documentation MUST be auto-generated (FastAPI OpenAPI)

**API Consistency Definition:**
"Consistent and predictable" means:
1. Same endpoint always returns same structure for same input
2. Field names use consistent casing (snake_case for API, camelCase for frontend)
3. Timestamps always in ISO 8601 format (e.g., "2026-02-03T10:30:00Z")
4. IDs always integers (not strings or UUIDs)
5. Pagination uses consistent query params: `?skip=0&limit=10`
6. Filtering uses consistent query params: `?completed=true`

**Meaningful Error Messages Definition:**
Error responses MUST include:
1. `detail`: Human-readable error description
2. `code`: Machine-readable error code (e.g., "INVALID_TOKEN", "TODO_NOT_FOUND")
3. `field`: (For validation errors) Which field caused the error
4. NO stack traces or internal error details

Example:
```json
{
  "detail": "Todo not found or you don't have permission to access it",
  "code": "TODO_NOT_FOUND"
}
```

**Business Logic Boundary Definition:**
- ✅ Frontend CAN: Render UI, handle forms, route navigation, display data
- ✅ Frontend CAN: Client-side validation (for UX, not security)
- ❌ Frontend CANNOT: Calculate derived values (e.g., total count, completion percentage)
- ❌ Frontend CANNOT: Filter/sort data (must request filtered data from API)
- ❌ Frontend CANNOT: Enforce business rules (e.g., "max 100 todos per user")

**Verification Checks:**
- ✅ PASS: FastAPI OpenAPI docs accessible at `/docs`
- ✅ PASS: All endpoints return JSON (Content-Type: application/json)
- ✅ PASS: All error responses include `detail` and `code` fields
- ✅ PASS: Frontend code contains no database imports or SQL
- ✅ PASS: Frontend code contains no business logic (only API calls and rendering)
- ❌ FAIL: Frontend calculates values that should come from API

**Rationale**: Clear separation of concerns enables independent development of
frontend and backend, facilitates testing, and ensures maintainability.

### VI. Secrets Management

All sensitive configuration MUST be managed via environment variables.

- No secrets, tokens, or credentials in source code
- No secrets in version control (use .env files, add to .gitignore)
- Environment variables MUST be documented in .env.example
- Production secrets MUST be managed via secure deployment platform
- Database connection strings MUST use environment variables
- JWT secrets MUST be stored in environment variables
- API keys MUST never be hardcoded

**Rationale**: Hardcoded secrets are a critical security vulnerability. Environment-based
configuration enables secure deployment across different environments and prevents
accidental exposure of credentials.

### VII. Stateless Architecture (NON-NEGOTIABLE - Phase III)

All backend services MUST be stateless with no in-memory state for chat or tool operations.

**Testable Requirements:**
- No in-memory chat history storage (must use database)
- No in-memory tool state or caching (must use database)
- Conversation history MUST be rebuilt from database on every request
- Server restart MUST NOT break ongoing conversations
- All chat messages MUST be persisted to database before response
- All tool execution results MUST be persisted to database
- No session state stored in backend memory (only JWT tokens)
- Database is the single source of truth for all conversation state

**Verification Checks:**
- ✅ PASS: Server restart → existing conversations still accessible
- ✅ PASS: No global variables or class-level state in chat/tool code
- ✅ PASS: All chat endpoints query database for conversation history
- ✅ PASS: All tool endpoints query database for task/todo data
- ❌ FAIL: Any in-memory cache, session store, or state dictionary detected

**Rationale**: Stateless architecture ensures scalability, reliability, and resilience.
In serverless/cloud environments, instances can be terminated at any time. Database-backed
persistence guarantees conversation continuity and enables horizontal scaling.

### VIII. MCP Tool Standards (NON-NEGOTIABLE - Phase III)

All Model Context Protocol (MCP) tools MUST be stateless, database-backed, and schema-validated.

**Testable Requirements:**
- Tools MUST be stateless (no internal state between calls)
- Tools MUST query database for all data (no caching)
- Tools MUST have explicit input schemas (Pydantic models)
- Tools MUST have explicit output schemas (Pydantic models)
- Tools MUST enforce user_id ownership (filter by authenticated user)
- Tools MUST validate all inputs before execution
- Tools MUST return structured responses (not plain text)
- Tools MUST handle errors gracefully with error codes

**Input Schema Requirements:**
```python
class ToolInput(BaseModel):
    user_id: int  # REQUIRED: authenticated user ID
    # ... other tool-specific fields with types and validation
```

**Output Schema Requirements:**
```python
class ToolOutput(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    error_code: Optional[str]
```

**Verification Checks:**
- ✅ PASS: All MCP tools have Pydantic input/output models
- ✅ PASS: All MCP tools include user_id in input schema
- ✅ PASS: All MCP tools filter database queries by user_id
- ✅ PASS: All MCP tools return structured JSON (not strings)
- ✅ PASS: Tool execution without user_id returns error
- ❌ FAIL: Any tool with untyped inputs or string-only outputs
- ❌ FAIL: Any tool that doesn't filter by user_id

**Rationale**: Explicit schemas enable validation, type safety, and clear contracts.
User_id enforcement prevents data leakage. Stateless tools ensure predictable behavior
and enable parallel execution.

### IX. Agent-Tool Interaction Rules (Phase III)

AI agents MUST use MCP tools for all task mutations and MUST NOT access database directly.

**Testable Requirements:**
- Agent MUST use MCP tools for all todo/task operations (create, read, update, delete)
- Agent MUST NOT import database models or execute SQL directly
- Agent MUST NOT bypass tool layer to access database
- Agent MUST request user confirmation before destructive actions (delete, bulk update)
- Agent MUST validate tool responses before presenting to user
- Agent MUST handle tool errors gracefully with user-friendly messages
- Agent MUST pass authenticated user_id to all tool calls

**Action Confirmation Requirements:**
Destructive actions requiring confirmation:
- Deleting todos (single or multiple)
- Marking all todos as complete/incomplete
- Clearing completed todos
- Any bulk operation affecting >1 todo

Confirmation format:
```
⚠️ Confirm action: [description]
- Affected items: [count]
- Action: [what will happen]
Type 'yes' to confirm or 'no' to cancel.
```

**Verification Checks:**
- ✅ PASS: Agent code contains no database imports (SQLModel, Session, etc.)
- ✅ PASS: Agent code contains no SQL queries
- ✅ PASS: All todo operations go through MCP tool calls
- ✅ PASS: Destructive actions show confirmation prompt
- ✅ PASS: Agent validates tool responses before using data
- ❌ FAIL: Agent imports database models or executes queries
- ❌ FAIL: Destructive action executes without confirmation

**Rationale**: Tool layer provides abstraction, validation, and security. Direct database
access bypasses validation and user_id filtering. Confirmations prevent accidental data loss.

## Testable Compliance Checks

### Security Verification (NON-NEGOTIABLE)

**Authentication Tests:**
- ✅ PASS: API returns 401 when Authorization header is missing
- ✅ PASS: API returns 401 when JWT token is malformed or expired
- ✅ PASS: API returns 401 when JWT signature is invalid
- ✅ PASS: Valid JWT allows access to protected endpoints
- ❌ FAIL: Any endpoint accepts requests without JWT (except public routes)

**Authorization Tests:**
- ✅ PASS: User A cannot access User B's todos (returns 403 or 404)
- ✅ PASS: Database queries include `WHERE user_id = <authenticated_user_id>`
- ✅ PASS: All SQLModel queries filter by authenticated user
- ❌ FAIL: Any query returns data from multiple users without explicit admin role

**Secrets Management Tests:**
- ✅ PASS: `git grep -i "password\|secret\|key" *.py *.ts *.tsx` returns no hardcoded values
- ✅ PASS: `.env.example` exists and documents all required environment variables
- ✅ PASS: `.env` is in `.gitignore`
- ✅ PASS: All secrets loaded from `os.getenv()` or `process.env`
- ❌ FAIL: Any hardcoded connection string, API key, or JWT secret found

**Chatbot Security Tests (Phase III):**
- ✅ PASS: All chat endpoints require valid JWT token
- ✅ PASS: All MCP tool calls include user_id from authenticated JWT
- ✅ PASS: Chat endpoint returns 401 when JWT is missing or invalid
- ✅ PASS: Tool calls with mismatched user_id (JWT vs request) return 403
- ✅ PASS: Conversation history filtered by authenticated user_id
- ❌ FAIL: Any chat/tool endpoint accepts requests without JWT
- ❌ FAIL: Any tool call bypasses user_id validation

### Phase III Compliance Checks (AI-Powered Chatbot)

### Stateless Architecture Verification (NON-NEGOTIABLE)

**No In-Memory State:**
- ✅ PASS: No global variables storing chat history
- ✅ PASS: No class-level state in chat/tool handlers
- ✅ PASS: No in-memory caching of conversations or tool results
- ✅ PASS: All chat endpoints query database for conversation history
- ❌ FAIL: Any in-memory session store, cache, or state dictionary

**Database-Backed Persistence:**
- ✅ PASS: All chat messages stored in database before response sent
- ✅ PASS: All tool execution results stored in database
- ✅ PASS: Conversation history rebuilt from database on every request
- ✅ PASS: Database has tables for: conversations, messages, tool_calls
- ❌ FAIL: Any chat data not persisted to database

**Server Restart Resilience:**
- ✅ PASS: Stop backend server → restart → existing conversations still accessible
- ✅ PASS: Stop backend server → restart → chat history intact
- ✅ PASS: Stop backend server → restart → tool execution history intact
- ❌ FAIL: Server restart causes conversation loss or corruption

### MCP Tool Verification

**Tool Schema Validation:**
- ✅ PASS: All MCP tools have Pydantic input models with explicit types
- ✅ PASS: All MCP tools have Pydantic output models with explicit types
- ✅ PASS: All tool input schemas include `user_id: int` field
- ✅ PASS: All tool output schemas include `success: bool` field
- ✅ PASS: Tool input validation rejects invalid types/missing fields
- ❌ FAIL: Any tool with untyped inputs (Dict[str, Any] without validation)
- ❌ FAIL: Any tool with string-only outputs (not structured JSON)

**Tool Statelessness:**
- ✅ PASS: Tools have no instance variables storing state
- ✅ PASS: Tools query database for all data (no caching)
- ✅ PASS: Same input always produces same output (idempotent where applicable)
- ✅ PASS: Tools can be called in any order without side effects
- ❌ FAIL: Tool behavior depends on previous calls or internal state

**User Ownership Enforcement:**
- ✅ PASS: All tool database queries include `WHERE user_id = <authenticated_user_id>`
- ✅ PASS: Tool call with user_id=1 cannot access user_id=2 data
- ✅ PASS: Tool call without user_id returns error (not default user)
- ✅ PASS: Tool call with mismatched user_id (JWT vs input) returns 403
- ❌ FAIL: Any tool query returns data from multiple users
- ❌ FAIL: Any tool accepts requests without user_id validation

### Agent-Tool Interaction Verification

**No Direct Database Access:**
- ✅ PASS: Agent code contains no `from sqlmodel import` or database imports
- ✅ PASS: Agent code contains no SQL queries or ORM calls
- ✅ PASS: Agent code contains no `Session()` or database connection code
- ✅ PASS: All todo operations use MCP tool calls (not direct DB access)
- ❌ FAIL: Agent imports database models or executes queries

**Tool Usage Compliance:**
- ✅ PASS: Agent uses MCP tools for all CRUD operations (create, read, update, delete)
- ✅ PASS: Agent validates tool responses before using data
- ✅ PASS: Agent handles tool errors gracefully with user-friendly messages
- ✅ PASS: Agent passes authenticated user_id to all tool calls
- ❌ FAIL: Agent bypasses tool layer for any database operation

**Action Confirmation:**
- ✅ PASS: Deleting todo shows confirmation prompt before execution
- ✅ PASS: Bulk operations (>1 item) show confirmation with affected count
- ✅ PASS: Confirmation includes clear description of action
- ✅ PASS: User can cancel destructive actions
- ❌ FAIL: Destructive action executes without user confirmation

### Conversation Persistence Verification

**Database Schema:**
- ✅ PASS: `conversations` table exists with columns: id, user_id, title, created_at, updated_at
- ✅ PASS: `messages` table exists with columns: id, conversation_id, role, content, created_at
- ✅ PASS: `tool_calls` table exists with columns: id, message_id, tool_name, input, output, created_at
- ✅ PASS: Foreign keys defined: messages.conversation_id → conversations.id
- ✅ PASS: Foreign keys defined: tool_calls.message_id → messages.id
- ✅ PASS: Indexes exist on user_id and conversation_id columns

**History Reconstruction:**
- ✅ PASS: Chat endpoint queries database for full conversation history
- ✅ PASS: Messages returned in chronological order (oldest first)
- ✅ PASS: Tool calls included in message history with results
- ✅ PASS: Conversation context includes all previous messages
- ❌ FAIL: Chat endpoint uses in-memory history instead of database

**Cross-Request Consistency:**
- ✅ PASS: Request 1 sends message → Request 2 sees that message in history
- ✅ PASS: Request 1 executes tool → Request 2 sees tool result in history
- ✅ PASS: Multiple concurrent requests to same conversation don't corrupt data
- ❌ FAIL: Messages or tool results lost between requests

### Code Hygiene Verification (Phase III)

**No Unused Files:**
- ✅ PASS: No unused Python files in backend/src/
- ✅ PASS: No unused TypeScript files in frontend/src/
- ✅ PASS: No commented-out code blocks (>10 lines)
- ✅ PASS: No TODO comments without corresponding GitHub issues
- ❌ FAIL: Unused imports, functions, or files detected

**Modular Structure:**
- ✅ PASS: MCP tools in separate module (e.g., backend/src/mcp_tools/)
- ✅ PASS: Chat logic in separate module (e.g., backend/src/chat/)
- ✅ PASS: Database models in separate module (e.g., backend/src/models/)
- ✅ PASS: Each module has single responsibility (no god files >500 lines)
- ✅ PASS: Clear separation: routes → services → tools → database
- ❌ FAIL: Mixed concerns (chat + tools + database in one file)

**Automated Checks:**
```bash
# Unused imports check
✅ PASS: pylint --disable=all --enable=unused-import backend/src/
✅ PASS: No unused imports detected

# Code complexity check
✅ PASS: All functions <50 lines (except generated code)
✅ PASS: All files <500 lines (except migrations)
✅ PASS: Cyclomatic complexity <10 per function

# Naming conventions
✅ PASS: All Python files use snake_case.py
✅ PASS: All TypeScript files use kebab-case.tsx or PascalCase.tsx (components)
✅ PASS: All functions/variables use snake_case (Python) or camelCase (TypeScript)
```

### API Contract Verification

**RESTful Conventions:**
- ✅ PASS: GET requests are idempotent (no side effects)
- ✅ PASS: POST creates resources, returns 201 with Location header
- ✅ PASS: PUT/PATCH updates resources, returns 200 or 204
- ✅ PASS: DELETE removes resources, returns 204
- ✅ PASS: All endpoints follow `/api/v1/<resource>` pattern

**Response Format Consistency:**
- ✅ PASS: Success responses return JSON with consistent schema
- ✅ PASS: Error responses follow format: `{"detail": "Error message", "code": "ERROR_CODE"}`
- ✅ PASS: All timestamps in ISO 8601 format
- ✅ PASS: All IDs are integers (not UUIDs or strings)
- ❌ FAIL: Inconsistent response structures across endpoints

**HTTP Status Codes:**
- ✅ PASS: 200 for successful GET/PUT/PATCH
- ✅ PASS: 201 for successful POST (resource created)
- ✅ PASS: 204 for successful DELETE (no content)
- ✅ PASS: 400 for validation errors (with field-level details)
- ✅ PASS: 401 for authentication failures
- ✅ PASS: 403 for authorization failures
- ✅ PASS: 404 for resource not found
- ✅ PASS: 500 for server errors (with generic message, no stack traces)

### Data Persistence Verification

**User Isolation:**
- ✅ PASS: Each todo has `user_id` foreign key to `user.id`
- ✅ PASS: All queries filter by authenticated user's ID
- ✅ PASS: User A's data never appears in User B's responses
- ❌ FAIL: Any cross-user data leakage detected

**Database Schema:**
- ✅ PASS: All tables have primary keys
- ✅ PASS: Foreign keys defined with proper constraints
- ✅ PASS: Indexes exist on `user_id` columns
- ✅ PASS: Migrations are reversible (up/down)
- ✅ PASS: No raw SQL strings (use SQLModel/Alembic)

### Frontend-Backend Integration

**API Communication:**
- ✅ PASS: Frontend includes JWT in `Authorization: Bearer <token>` header
- ✅ PASS: Frontend handles 401 by redirecting to login
- ✅ PASS: Frontend handles 403 with appropriate error message
- ✅ PASS: Frontend displays validation errors from 400 responses
- ❌ FAIL: Frontend makes direct database calls

**Business Logic Boundary:**
- ✅ PASS: Frontend only contains presentation logic (rendering, form handling, routing)
- ✅ PASS: All data validation happens in backend (Pydantic models)
- ✅ PASS: All data transformations happen in backend
- ❌ FAIL: Frontend contains business rules (e.g., calculating totals, filtering by status)

### Technology Stack Verification

**Automated Checks:**
```bash
# Frontend stack verification
✅ PASS: package.json includes "next": "^16.0.0"
✅ PASS: package.json includes "tailwindcss"
✅ PASS: All .tsx files use TypeScript
✅ PASS: app/ directory exists (App Router)
❌ FAIL: pages/ directory exists (Pages Router prohibited)

# Backend stack verification
✅ PASS: requirements.txt includes "fastapi"
✅ PASS: requirements.txt includes "sqlmodel"
✅ PASS: requirements.txt includes "python-jose"
✅ PASS: All .py files use FastAPI decorators
❌ FAIL: Flask, Django, or other frameworks detected

# Database verification
✅ PASS: DATABASE_URL contains "neon.tech"
✅ PASS: Alembic migrations directory exists
✅ PASS: SQLModel models use table=True
❌ FAIL: MongoDB, MySQL, or SQLite imports detected
```

## Definition of Done

### Phase II: Hackathon MVP Criteria (Web Application)

The Phase II project is considered **DONE** when all of the following are met:

**Functional Requirements:**
1. ✅ User can sign up with email/password (Better Auth)
2. ✅ User can sign in and receive JWT token
3. ✅ User can create a new todo item
4. ✅ User can view their own todo list (filtered by user_id)
5. ✅ User can mark todo as complete/incomplete
6. ✅ User can delete their own todo
7. ✅ User cannot see or modify other users' todos

**Technical Requirements:**
1. ✅ All API endpoints require valid JWT (except signup/signin)
2. ✅ All database queries filter by authenticated user ID
3. ✅ Frontend built with Next.js App Router + Tailwind CSS
4. ✅ Backend built with FastAPI + SQLModel
5. ✅ Database is Neon Serverless PostgreSQL
6. ✅ No hardcoded secrets (all in environment variables)
7. ✅ All code generated via Claude Code (traceable to specs/plans/tasks)

**Documentation Requirements:**
1. ✅ Feature spec exists in `specs/<feature>/spec.md`
2. ✅ Implementation plan exists in `specs/<feature>/plan.md`
3. ✅ Task list exists in `specs/<feature>/tasks.md`
4. ✅ `.env.example` documents all required environment variables
5. ✅ README.md includes setup instructions

**Security Requirements:**
1. ✅ All security verification tests pass (see Testable Compliance Checks)
2. ✅ Auth Agent has audited authentication implementation
3. ✅ No secrets in git history (`git log -p | grep -i "password\|secret"` returns nothing)

**Deployment Readiness:**
1. ✅ Frontend runs on `localhost:3000` (or deployed URL)
2. ✅ Backend runs on `localhost:8000` (or deployed URL)
3. ✅ Database migrations applied successfully
4. ✅ CORS configured for frontend-backend communication

### Phase III: AI-Powered Chatbot Criteria

The Phase III project is considered **DONE** when all Phase II criteria are met PLUS:

**Functional Requirements:**
1. ✅ User can start a new chat conversation
2. ✅ User can send messages to AI chatbot
3. ✅ Chatbot can list user's todos via MCP tool
4. ✅ Chatbot can create new todos via MCP tool
5. ✅ Chatbot can mark todos complete/incomplete via MCP tool
6. ✅ Chatbot can delete todos via MCP tool (with confirmation)
7. ✅ User can view chat history (persisted across sessions)
8. ✅ User cannot access other users' conversations

**Technical Requirements:**
1. ✅ All chat endpoints require valid JWT authentication
2. ✅ All MCP tools are stateless and database-backed
3. ✅ All MCP tools have explicit Pydantic input/output schemas
4. ✅ All MCP tools enforce user_id ownership
5. ✅ Conversation history rebuilt from database on every request
6. ✅ Server restart does NOT break ongoing conversations
7. ✅ Agent uses MCP tools for all todo operations (no direct DB access)
8. ✅ Destructive actions require user confirmation

**Stateless Architecture Requirements:**
1. ✅ No in-memory chat history storage
2. ✅ No in-memory tool state or caching
3. ✅ All chat messages persisted to database before response
4. ✅ All tool execution results persisted to database
5. ✅ Database is single source of truth for conversation state

**MCP Tool Requirements:**
1. ✅ All tools have Pydantic input models with user_id field
2. ✅ All tools have Pydantic output models with success field
3. ✅ All tools filter database queries by user_id
4. ✅ All tools return structured JSON (not plain text)
5. ✅ Tool schemas documented in code and API docs

**Security Requirements:**
1. ✅ All Phase III security verification tests pass
2. ✅ Chat endpoints return 401 when JWT missing/invalid
3. ✅ Tool calls with mismatched user_id return 403
4. ✅ Conversation history filtered by authenticated user_id
5. ✅ No cross-user conversation access possible

**Code Hygiene Requirements:**
1. ✅ No unused files or artifacts in codebase
2. ✅ Modular structure (tools, chat, models in separate modules)
3. ✅ No commented-out code blocks (>10 lines)
4. ✅ All functions <50 lines (except generated code)
5. ✅ All files <500 lines (except migrations)

**Documentation Requirements:**
1. ✅ Phase III feature spec exists
2. ✅ Phase III implementation plan exists
3. ✅ Phase III task list exists
4. ✅ MCP tool schemas documented
5. ✅ Chat API endpoints documented

### Out of Scope (Explicitly NOT Required)

**Phase II (Web Application):**
- ❌ User profile editing
- ❌ Password reset functionality
- ❌ Email verification
- ❌ Todo categories or tags
- ❌ Todo due dates or priorities
- ❌ Sharing todos with other users
- ❌ Real-time updates (WebSockets)
- ❌ Mobile app
- ❌ Automated tests (unit/integration)
- ❌ CI/CD pipeline
- ❌ Production deployment

**Phase III (AI Chatbot):**
- ❌ Voice input/output
- ❌ Multi-language support
- ❌ Conversation branching or forking
- ❌ Exporting chat history
- ❌ Sharing conversations with other users
- ❌ Custom AI personalities or system prompts
- ❌ Image/file uploads in chat
- ❌ Advanced NLP features (sentiment analysis, summarization)
- ❌ Integration with external services (calendar, email, etc.)
- ❌ Automated tests for chatbot responses
- ❌ Performance benchmarking or load testing

## Technology Stack Requirements

### Mandatory Technologies

**Frontend Stack (Phase II & III):**
- Framework: Next.js 16+ (App Router only)
- Styling: Tailwind CSS
- Language: TypeScript
- State Management: React hooks (useState, useContext)
- Data Fetching: Server Components with async/await

**Backend Stack (Phase II & III):**
- Framework: Python FastAPI
- ORM: SQLModel
- Validation: Pydantic (included in SQLModel)
- Authentication: python-jose for JWT
- Server: Uvicorn (ASGI server)

**Database Stack (Phase II & III):**
- Database: Neon Serverless PostgreSQL
- Connection Pooling: PgBouncer (recommended)
- Migrations: Alembic
- Query Builder: SQLModel select()

**Authentication Stack (Phase II & III):**
- Frontend: Better Auth
- Backend: JWT token verification
- Token Format: JSON Web Tokens (JWT)
- Algorithm: HS256 (HMAC with SHA-256)

**AI Chatbot Stack (Phase III):**
- AI Provider: Anthropic Claude API
- Models: claude-3-5-sonnet-20241022 (primary) or claude-3-5-haiku-20241022 (fast responses)
- SDK: anthropic Python package
- Tool Protocol: Model Context Protocol (MCP)
- Tool Schemas: Pydantic models for input/output validation
- Streaming: Server-Sent Events (SSE) for real-time responses
- Conversation Storage: PostgreSQL (conversations, messages, tool_calls tables)

### Prohibited Technologies

**General Prohibitions:**
- No other frontend frameworks (React without Next.js, Vue, Angular, etc.)
- No other CSS frameworks (Bootstrap, Material-UI, etc.)
- No other backend frameworks (Django, Flask, Express, etc.)
- No other ORMs (raw SQLAlchemy, Prisma, TypeORM, etc.)
- No other databases (MongoDB, MySQL, SQLite, etc.)
- No session-based authentication (only JWT)

**Phase III Prohibitions:**
- No other AI providers (OpenAI, Cohere, etc.) - only Anthropic Claude
- No LangChain or similar frameworks (use direct Claude SDK + MCP)
- No in-memory conversation storage (Redis, Memcached, etc.)
- No WebSocket-based chat (use HTTP + SSE for streaming)
- No custom tool protocols (only MCP standard)

## Development Workflow

### Spec-Driven Process

1. **Specification Phase** (`/sp.specify`)
   - Write feature specification in `specs/<feature>/spec.md`
   - Define requirements, acceptance criteria, and constraints
   - Get user approval before proceeding

2. **Planning Phase** (`/sp.plan`)
   - Create architectural plan in `specs/<feature>/plan.md`
   - Define API contracts, data models, and component structure
   - Identify architectural decisions requiring ADRs
   - Get user approval before proceeding

3. **Task Breakdown Phase** (`/sp.tasks`)
   - Generate task list in `specs/<feature>/tasks.md`
   - Break plan into atomic, testable tasks
   - Define acceptance criteria for each task
   - Order tasks by dependencies

4. **Implementation Phase** (`/sp.implement`)
   - Execute tasks sequentially using appropriate agents
   - Use Frontend Agent for Next.js components
   - Use Backend Agent for FastAPI endpoints
   - Use Database Agent for schema and migrations
   - Use Auth Agent for authentication/authorization
   - Create PHR (Prompt History Record) for each significant interaction

5. **Verification Phase**
   - Run tests for each completed task
   - Verify acceptance criteria met
   - Ensure security requirements satisfied
   - Check constitution compliance

### Agent Usage

**Frontend Agent** (`frontend-agent`):
- Use for: Next.js pages, components, layouts, Tailwind styling
- Required Skill: Frontend Skill
- Responsibilities: UI/UX, client-side logic, API integration

**Backend Agent** (`fastapi-backend-agent`):
- Use for: FastAPI routes, request/response models, business logic
- Required Skill: Backend Skill
- Responsibilities: API endpoints, validation, error handling

**Database Agent** (`database-agent`):
- Use for: Schema design, migrations, query optimization
- Required Skill: Database Skill
- Responsibilities: Data modeling, database operations, indexing

**Auth Agent** (`auth-security-auditor`):
- Use for: Authentication flows, JWT verification, security audits
- Required Skill: Auth Skill
- Responsibilities: Security implementation, token handling, authorization

### Multi-Agent Coordination

**Phase II (Web Application) - Coordinate agents in this order:**
1. **Database Agent** → Design schema and tables
2. **Backend Agent** → Create API endpoints with database integration
3. **Auth Agent** → Add authentication/authorization to endpoints
4. **Frontend Agent** → Build UI that consumes the APIs

**Phase III (AI Chatbot) - Coordinate agents in this order:**
1. **Database Agent** → Design conversation/message/tool_calls schema
2. **Backend Agent** → Create MCP tool endpoints with explicit schemas
3. **Backend Agent** → Create chat endpoint with Claude SDK integration
4. **Auth Agent** → Add JWT authentication to chat and tool endpoints
5. **Frontend Agent** → Build chat UI with streaming support
6. **Code Quality Agent** → Review for stateless architecture compliance

**Phase III Specific Guidelines:**
- MCP tools MUST be implemented before chat endpoint (tools are dependencies)
- All tools MUST be tested independently before agent integration
- Stateless architecture MUST be verified after each implementation
- Conversation persistence MUST be tested with server restart scenarios

## Governance

### Constitution Authority

This constitution supersedes all other development practices, guidelines, or
conventions. In case of conflict, constitution principles take precedence.

### Compliance Requirements

- All pull requests MUST verify constitution compliance
- All code reviews MUST check adherence to core principles
- All architectural decisions MUST align with technology stack requirements
- All security implementations MUST follow security-first architecture
- Violations MUST be documented and remediated immediately

### Amendment Process

1. Propose amendment with clear rationale
2. Document impact on existing code and processes
3. Update dependent templates and documentation
4. Increment version according to semantic versioning:
   - MAJOR: Backward-incompatible principle changes
   - MINOR: New principles or sections added
   - PATCH: Clarifications, wording improvements
5. Create ADR for significant governance changes
6. Update this file with sync impact report

### Version Control

All constitution changes MUST be version controlled with:
- Clear commit messages describing changes
- Sync impact report at top of file
- Updated version number and amendment date
- PHR documenting the amendment process

### Enforcement

- Automated checks SHOULD verify technology stack adherence
- Code generation MUST use specified agents and skills
- Security audits MUST be performed for authentication code
- Constitution violations MUST be treated as critical issues

**Version**: 1.2.0 | **Ratified**: 2026-02-03 | **Last Amended**: 2026-02-09
