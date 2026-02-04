# Implementation Plan: Backend JWT Authentication & API Security

**Branch**: `002-backend-jwt-auth` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-backend-jwt-auth/spec.md`

## Summary

Secure the existing FastAPI backend with JWT token authentication issued by Better Auth. Implement middleware to validate JWT tokens on every request, extract user identity from the "sub" claim, and automatically provision user records in the database on first authentication. Enforce strict user isolation by filtering all task queries by authenticated user ID, ensuring users can only access their own data. The backend remains stateless, deriving all user identity from JWT tokens without server-side sessions.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel, python-jose[cryptography], psycopg2-binary, python-dotenv
**Storage**: Neon Serverless PostgreSQL with connection pooling
**Testing**: Manual API testing via FastAPI `/docs` endpoint, pytest for future automated tests
**Target Platform**: Linux/Windows server (development), serverless deployment (production)
**Project Type**: Web backend API
**Performance Goals**: <50ms authentication overhead, support 1000 concurrent authenticated requests
**Constraints**: Stateless architecture (no server-side sessions), JWT-only authentication, strict user isolation
**Scale/Scope**: Multi-user todo application, ~10 API endpoints, 2 database tables (users, tasks)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Security-First Architecture (NON-NEGOTIABLE)
- ✅ **PASS**: All API routes will require valid JWT authentication (middleware enforces globally)
- ✅ **PASS**: JWT tokens verified on every backend request (middleware validates signature and expiration)
- ✅ **PASS**: User data strictly isolated (all queries filter by authenticated user_id)
- ✅ **PASS**: Database queries filter by authenticated user ID (SQLModel queries include WHERE user_id = ...)
- ✅ **PASS**: No hardcoded secrets (JWT_SECRET from environment variable)
- ✅ **PASS**: Authentication failures return 401 Unauthorized
- ✅ **PASS**: Authorization failures return 404 Not Found (to prevent information leakage)

### Technology Stack Adherence
- ✅ **PASS**: Backend uses Python FastAPI (no other frameworks)
- ✅ **PASS**: ORM uses SQLModel (combines SQLAlchemy + Pydantic)
- ✅ **PASS**: Database is Neon Serverless PostgreSQL
- ✅ **PASS**: JWT handling uses python-jose (standard library for JWT in Python)
- ✅ **PASS**: All code generated via Claude Code (traceable to specs/plans/tasks)

### API Contract Discipline
- ✅ **PASS**: All endpoints follow RESTful conventions (GET /tasks, POST /tasks, etc.)
- ✅ **PASS**: Request/response schemas defined with Pydantic/SQLModel
- ✅ **PASS**: Error responses include meaningful messages with "detail" and "code" fields
- ✅ **PASS**: API documentation auto-generated (FastAPI OpenAPI at /docs)
- ✅ **PASS**: Standard HTTP status codes (401 for auth failures, 404 for not found, 500 for server errors)

### Secrets Management
- ✅ **PASS**: JWT secret stored in environment variable (JWT_SECRET)
- ✅ **PASS**: Database connection string from environment (DATABASE_URL)
- ✅ **PASS**: .env.example documents all required variables
- ✅ **PASS**: .env in .gitignore

### Spec-Driven Development
- ✅ **PASS**: Feature spec exists at specs/002-backend-jwt-auth/spec.md
- ✅ **PASS**: Implementation plan (this file) derived from spec
- ✅ **PASS**: Tasks will be broken down from this plan (via /sp.tasks)
- ✅ **PASS**: PHR will be created for implementation sessions

**Constitution Compliance**: ✅ ALL GATES PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/002-backend-jwt-auth/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (JWT best practices, middleware patterns)
├── data-model.md        # Phase 1 output (User and Task models)
├── quickstart.md        # Phase 1 output (setup and testing guide)
├── contracts/           # Phase 1 output (API endpoint contracts)
│   ├── auth.yaml        # Authentication endpoints (if any)
│   └── tasks.yaml       # Task CRUD endpoints with auth
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization, CORS, middleware registration
│   ├── config.py               # Environment variable loading (JWT_SECRET, DATABASE_URL)
│   ├── database.py             # Database connection, session management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User SQLModel (id, email, name, avatar_url, timestamps)
│   │   └── task.py             # Task SQLModel (updated with user_id foreign key)
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py             # JWT verification middleware, user provisioning
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py             # Dependency to get current user from request state
│   ├── routers/
│   │   ├── __init__.py
│   │   └── tasks.py            # Task CRUD endpoints (updated with user filtering)
│   └── schemas/
│       ├── __init__.py
│       ├── user.py             # User Pydantic schemas (response models)
│       └── task.py             # Task Pydantic schemas (request/response models)
├── alembic/
│   ├── versions/
│   │   └── [timestamp]_add_users_table.py  # Migration to create users table
│   └── env.py
├── tests/
│   ├── __init__.py
│   └── test_auth.py            # Manual test cases (future automated tests)
├── .env.example                # Documents JWT_SECRET, DATABASE_URL
├── .env                        # Local secrets (gitignored)
├── requirements.txt            # Python dependencies
└── README.md                   # Setup instructions
```

**Structure Decision**: Web application backend structure selected. The backend/ directory contains the FastAPI application with clear separation of concerns: models (database), middleware (authentication), dependencies (request context), routers (endpoints), and schemas (API contracts). This structure follows FastAPI best practices and enables clear agent coordination (Database Agent for models, Auth Agent for middleware, Backend Agent for routers).

## Complexity Tracking

> **No violations detected** - All constitution requirements satisfied without exceptions.

## Phase 0: Research & Unknowns Resolution

### Research Topics

1. **JWT Verification Best Practices in FastAPI**
   - How to implement middleware vs dependency injection for JWT verification
   - Performance implications of middleware vs per-route dependencies
   - Error handling patterns for authentication failures

2. **Lazy User Provisioning Patterns**
   - Race condition handling when multiple requests arrive for new user
   - Database transaction strategies (optimistic vs pessimistic locking)
   - Idempotency patterns for user creation

3. **SQLModel User Isolation Patterns**
   - Best practices for filtering queries by user_id
   - Performance optimization with indexes on user_id columns
   - Preventing N+1 queries with relationship loading

4. **python-jose JWT Configuration**
   - Supported algorithms (HS256, RS256)
   - Token expiration validation
   - Custom claims extraction (sub, email, name)

### Research Execution

✅ **COMPLETED**: All research topics resolved in [research.md](./research.md)

**Key Decisions**:
1. **JWT Verification**: Middleware + Dependency hybrid pattern
2. **User Provisioning**: Database constraint + exception handling (idempotent)
3. **User Isolation**: Query filtering with WHERE clauses + database indexes
4. **JWT Configuration**: HS256 algorithm with shared secret
5. **Error Responses**: Structured with detail and code fields
6. **Logging**: Authentication failures only (security monitoring)

---

## Phase 1: Design & Contracts

### Data Model

✅ **COMPLETED**: Entity definitions in [data-model.md](./data-model.md)

**Entities Defined**:
- **User**: id (PK), email (UNIQUE), name, avatar_url, timestamps
- **Task**: id (PK), user_id (FK), title, description, completed, priority, due_date, timestamps

**Relationships**:
- User (1) ──────< (Many) Task
- Foreign key: tasks.user_id → users.id (ON DELETE CASCADE)

**Indexes**:
- users.id (PRIMARY KEY)
- users.email (UNIQUE INDEX)
- tasks.user_id (INDEX for user-scoped queries)
- tasks.(id, user_id) (COMPOSITE INDEX for single-task lookups)

**Migrations**:
1. Create users table with constraints
2. Add user_id column to tasks table with foreign key

### API Contracts

✅ **COMPLETED**: OpenAPI specification in [contracts/tasks.yaml](./contracts/tasks.yaml)

**Endpoints Defined**:
- `GET /tasks` - Get all tasks for authenticated user (with optional filters)
- `POST /tasks` - Create new task for authenticated user
- `GET /tasks/{task_id}` - Get specific task (if owned by user)
- `PUT /tasks/{task_id}` - Update task (if owned by user)
- `DELETE /tasks/{task_id}` - Delete task (if owned by user)

**Authentication**:
- All endpoints require `Authorization: Bearer <jwt-token>` header
- 401 Unauthorized for missing/invalid tokens
- 404 Not Found for unauthorized access (prevents information leakage)

**Request/Response Schemas**:
- TaskCreate: title (required), description, priority, due_date
- TaskUpdate: title, description, completed, priority, due_date (all optional)
- Task: Full task object with id, user_id, timestamps
- Error: Structured error with detail and code fields

### Quickstart Guide

✅ **COMPLETED**: Setup and testing instructions in [quickstart.md](./quickstart.md)

**Includes**:
- Environment setup (dependencies, .env configuration)
- Database migrations (Alembic commands)
- Server startup instructions
- Manual testing via FastAPI /docs
- Testing with cURL commands
- Verification checklist (authentication, user isolation, security)
- Troubleshooting guide

### Agent Context Update

✅ **COMPLETED**: Updated CLAUDE.md with new technologies

**Added**:
- Python 3.11+ + FastAPI, SQLModel, python-jose[cryptography], psycopg2-binary, python-dotenv
- Neon Serverless PostgreSQL with connection pooling

---

## Phase 2: Constitution Re-Check

*Re-evaluating constitution compliance after design phase*

### Security-First Architecture (NON-NEGOTIABLE)
- ✅ **PASS**: All API routes require JWT authentication (middleware enforces globally)
- ✅ **PASS**: JWT tokens verified on every request (middleware validates signature and expiration)
- ✅ **PASS**: User data strictly isolated (all queries filter by user_id with WHERE clauses)
- ✅ **PASS**: Database queries filter by authenticated user ID (SQLModel select() with WHERE)
- ✅ **PASS**: No hardcoded secrets (JWT_SECRET and DATABASE_URL from environment)
- ✅ **PASS**: Authentication failures return 401 Unauthorized with structured errors
- ✅ **PASS**: Authorization failures return 404 Not Found (prevents information leakage)

### Technology Stack Adherence
- ✅ **PASS**: Backend uses Python FastAPI exclusively
- ✅ **PASS**: ORM uses SQLModel (combines SQLAlchemy + Pydantic)
- ✅ **PASS**: Database is Neon Serverless PostgreSQL with connection pooling
- ✅ **PASS**: JWT handling uses python-jose[cryptography]
- ✅ **PASS**: All code will be generated via Claude Code (Auth Agent, Backend Agent, Database Agent)

### API Contract Discipline
- ✅ **PASS**: All endpoints follow RESTful conventions (GET, POST, PUT, DELETE)
- ✅ **PASS**: Request/response schemas defined with Pydantic/SQLModel
- ✅ **PASS**: Error responses include "detail" and "code" fields
- ✅ **PASS**: API documentation auto-generated (FastAPI OpenAPI at /docs)
- ✅ **PASS**: Standard HTTP status codes (200, 201, 204, 400, 401, 404, 500)
- ✅ **PASS**: Consistent response format (JSON with snake_case fields)
- ✅ **PASS**: Timestamps in ISO 8601 format

### Secrets Management
- ✅ **PASS**: JWT_SECRET stored in environment variable
- ✅ **PASS**: DATABASE_URL stored in environment variable
- ✅ **PASS**: .env.example documents all required variables
- ✅ **PASS**: .env in .gitignore (no secrets in version control)

### Spec-Driven Development
- ✅ **PASS**: Feature spec exists at specs/002-backend-jwt-auth/spec.md
- ✅ **PASS**: Implementation plan (this file) derived from spec
- ✅ **PASS**: Research completed and documented
- ✅ **PASS**: Data model designed and documented
- ✅ **PASS**: API contracts defined in OpenAPI format
- ✅ **PASS**: Quickstart guide created for implementation
- ✅ **PASS**: Tasks will be broken down from this plan (via /sp.tasks)

**Final Constitution Compliance**: ✅ ALL GATES PASSED - Ready for task breakdown

---

## Implementation Strategy

### Agent Coordination

**Phase 1: Database Foundation** (Database Agent)
1. Create User SQLModel with all fields and constraints
2. Update Task SQLModel with user_id foreign key
3. Create Alembic migration for users table
4. Create Alembic migration for adding user_id to tasks
5. Apply migrations and verify schema

**Phase 2: Authentication Layer** (Auth Agent)
1. Implement JWT verification middleware
2. Implement user provisioning logic (idempotent, race-condition safe)
3. Implement get_current_user dependency
4. Add authentication failure logging
5. Test authentication with valid/invalid/expired tokens

**Phase 3: API Endpoints** (Backend Agent)
1. Update task router to use get_current_user dependency
2. Add user_id filtering to all task queries
3. Update task creation to set user_id from authenticated user
4. Update error responses to use structured format
5. Test all endpoints with user isolation

**Phase 4: Integration Testing** (Manual)
1. Test authentication flow end-to-end
2. Test user provisioning (first-time and subsequent)
3. Test user isolation (cross-user access attempts)
4. Test error handling (401, 404, 400, 500)
5. Verify performance (<50ms auth overhead)

### Critical Path

```
Database Schema → JWT Middleware → User Provisioning → API Endpoints → Testing
     (Day 1)          (Day 1)           (Day 2)            (Day 2)       (Day 3)
```

### Risk Mitigation

**Risk 1: JWT_SECRET mismatch between Better Auth and FastAPI**
- Mitigation: Document clearly in .env.example and quickstart.md
- Validation: Test with actual Better Auth token before proceeding

**Risk 2: Race conditions in user provisioning**
- Mitigation: Use database UNIQUE constraint + exception handling
- Validation: Concurrent request testing (10 simultaneous requests)

**Risk 3: User isolation bypass**
- Mitigation: Mandatory user_id filtering in all queries
- Validation: Cross-user access testing with multiple users

**Risk 4: Performance degradation from JWT verification**
- Mitigation: Middleware pattern (verify once per request)
- Validation: Load testing with 1000 concurrent requests

---

## Architectural Decisions

### ADR Candidates

The following decisions may warrant Architecture Decision Records (ADRs):

1. **JWT Verification Pattern: Middleware + Dependency Hybrid**
   - Decision: Use middleware for global JWT validation, dependency for route access
   - Rationale: Performance (verify once) + type safety (dependency injection)
   - Alternatives: Dependency-only (inefficient), middleware-only (not type-safe)

2. **User Provisioning Strategy: Lazy Creation with Database Constraints**
   - Decision: Auto-create users on first authentication using DB constraints
   - Rationale: Idempotent, handles race conditions, no application-level locking
   - Alternatives: Pre-populated users (requires sync), pessimistic locking (complex)

3. **User Isolation: Query-Level Filtering**
   - Decision: Add WHERE user_id = <auth_user> to all task queries
   - Rationale: Secure, performant with indexes, prevents cross-user access
   - Alternatives: Row-level security (complex), application-level filtering (error-prone)

4. **Error Response: 404 for Unauthorized Access**
   - Decision: Return 404 (not 403) when user accesses another user's task
   - Rationale: Prevents information leakage about existence of other users' data
   - Alternatives: 403 Forbidden (leaks information), 401 (incorrect semantic)

**Recommendation**: Create ADRs for decisions 1, 2, and 4 during implementation phase.

---

## Success Criteria

This plan is considered complete when:

- ✅ All research topics resolved (research.md)
- ✅ Data model designed with entities and relationships (data-model.md)
- ✅ API contracts defined in OpenAPI format (contracts/tasks.yaml)
- ✅ Quickstart guide created with setup and testing instructions (quickstart.md)
- ✅ Agent context updated with new technologies (CLAUDE.md)
- ✅ Constitution compliance verified (all gates passed)
- ✅ Implementation strategy defined with agent coordination
- ✅ Critical path and risk mitigation documented
- ✅ ADR candidates identified

**Status**: ✅ PLAN COMPLETE - Ready for `/sp.tasks` command

---

## Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to break down this plan into atomic, testable tasks
2. **Implement**: Execute tasks using specialized agents:
   - Database Agent for schema and migrations
   - Auth Agent for JWT middleware and user provisioning
   - Backend Agent for API endpoint updates
3. **Security Audit**: Use Auth Agent to review authentication implementation
4. **Integration Test**: Test with actual Better Auth frontend
5. **Create ADRs**: Document architectural decisions 1, 2, and 4

**Estimated Implementation Time**: 2-3 days (assuming 8-hour workdays)

**Blocking Dependencies**: None - all prerequisites satisfied

