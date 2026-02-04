# Implementation Plan: Backend Core – Task API & Database Layer

**Branch**: `001-backend-task-api` | **Date**: 2026-02-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-task-api/spec.md`

## Summary

Build a FastAPI backend service that provides RESTful CRUD operations for task management with persistent storage in Neon Serverless PostgreSQL. The system uses SQLModel for ORM, supports all standard task operations (create, read, update, delete, complete), and includes a user_id field for future authentication integration. This phase explicitly excludes JWT authentication enforcement but ensures the data model and API structure are compatible with future auth implementation.

**Primary Requirement**: Deliver functional REST API endpoints for task management with database persistence.

**Technical Approach**: Incremental layered build starting with database models, then API endpoints, followed by validation and error handling. Each layer is validated before proceeding to the next.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel, Uvicorn (ASGI server), psycopg2-binary, python-dotenv, python-jose (for future JWT)
**Storage**: Neon Serverless PostgreSQL (cloud-hosted)
**Testing**: Manual API verification via FastAPI auto-generated docs (/docs endpoint)
**Target Platform**: Linux/Windows server (local development), cloud deployment ready
**Project Type**: Backend API service (single service, no frontend in this feature)
**Performance Goals**: <200ms response time for 95% of requests, handle 100+ concurrent requests
**Constraints**: <200ms p95 latency, environment-based configuration only, no hardcoded secrets
**Scale/Scope**: Hackathon MVP - moderate load (<1000 concurrent users), 6 API endpoints, 1 database table

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development
- ✅ PASS: Specification exists at specs/001-backend-task-api/spec.md
- ✅ PASS: Plan being created at specs/001-backend-task-api/plan.md
- ✅ PASS: Tasks will be generated via /sp.tasks after plan approval
- ✅ PASS: Implementation will follow task list via /sp.implement

### Principle II: Zero Manual Coding
- ✅ PASS: All code will be generated via Claude Code
- ✅ PASS: Backend Agent will be used for FastAPI implementation
- ✅ PASS: Database Agent will be used for schema design
- ✅ PASS: All changes traceable to spec/plan/tasks

### Principle III: Security-First Architecture
- ⚠️ DEFERRED: JWT authentication explicitly NOT enforced in this phase (per spec)
- ✅ PASS: user_id field included in data model for future auth integration
- ✅ PASS: No hardcoded secrets (DATABASE_URL from environment)
- ✅ PASS: Error messages will not expose sensitive information
- ✅ PASS: All secrets managed via environment variables

**Justification for deferred auth**: Specification explicitly states "Authentication: Not enforced" as a scope constraint. This is Phase 1 of a multi-phase implementation. Future phase will add JWT verification using Auth Agent.

### Principle IV: Technology Stack Adherence
- ✅ PASS: Backend framework is Python FastAPI (required)
- ✅ PASS: ORM is SQLModel (required)
- ✅ PASS: Database is Neon Serverless PostgreSQL (required)
- ✅ PASS: API style is RESTful, JSON-based (required)
- ✅ PASS: Configuration via environment variables only (required)

### Principle V: API Contract Discipline
- ✅ PASS: All endpoints follow RESTful conventions
- ✅ PASS: Request/response schemas defined with Pydantic/SQLModel
- ✅ PASS: Standard HTTP status codes (200, 201, 204, 400, 404, 500)
- ✅ PASS: Error responses include detail and code fields
- ✅ PASS: API documentation auto-generated (FastAPI OpenAPI)

### Principle VI: Secrets Management
- ✅ PASS: DATABASE_URL loaded from environment variable
- ✅ PASS: No hardcoded credentials in code
- ✅ PASS: .env.example will document required variables
- ✅ PASS: .env added to .gitignore

**Constitution Compliance**: ✅ ALL GATES PASS (1 deferred with justification)

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-task-api/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── openapi.yaml     # OpenAPI 3.0 specification
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variable template
├── .env                      # Local environment variables (gitignored)
├── core/
│   ├── __init__.py
│   ├── config.py             # Settings and environment variable loading
│   └── database.py           # Database engine and session management
├── models/
│   ├── __init__.py
│   └── task.py               # SQLModel Task model (table=True)
├── schemas/
│   ├── __init__.py
│   └── task.py               # Pydantic request/response schemas
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── endpoints/
│           ├── __init__.py
│           └── tasks.py      # Task CRUD endpoints
└── alembic/                  # Database migrations (future)
    └── versions/
```

**Structure Decision**: Backend-only structure selected because this feature implements only the API layer. Frontend will be a separate feature. The structure follows FastAPI best practices with clear separation of concerns:
- `core/`: Configuration and database setup
- `models/`: SQLModel database models
- `schemas/`: Pydantic request/response models
- `api/v1/endpoints/`: API route handlers

## Complexity Tracking

No complexity violations. All constitution gates pass or are deferred with clear justification.

---

## Phase 0: Research & Decisions

### Research Tasks

1. **Database Schema Design**
   - Decision: Use integer primary key for task.id, integer for user_id
   - Rationale: Simpler than UUIDs, sufficient for hackathon scale, better performance for joins
   - Alternatives: UUIDs (more scalable but overkill for MVP), string IDs (less efficient)

2. **SQLModel vs Raw SQL**
   - Decision: Use SQLModel exclusively (no raw SQL)
   - Rationale: Type safety, automatic validation, cleaner code, easier to maintain
   - Alternatives: Raw SQL (more control but verbose), SQLAlchemy Core (middle ground)

3. **user_id Representation**
   - Decision: Integer type, required field, no foreign key constraint yet
   - Rationale: Simple, compatible with future auth, no user table needed in this phase
   - Alternatives: UUID (overkill), string (less efficient), foreign key (requires user table)

4. **Error Handling Strategy**
   - Decision: Use FastAPI HTTPException with detail and custom error codes
   - Rationale: Standard FastAPI pattern, consistent error format, easy to extend
   - Alternatives: Custom exception classes (more complex), plain HTTP responses (less structured)

5. **Environment Variable Management**
   - Decision: Use python-dotenv to load .env file, pydantic Settings for validation
   - Rationale: Standard Python pattern, type-safe, easy to test
   - Alternatives: os.getenv() directly (no validation), config files (less secure)

6. **Connection Pooling for Neon**
   - Decision: Use SQLModel's default connection pooling with pool_pre_ping=True
   - Rationale: Handles serverless cold starts, verifies connections before use
   - Alternatives: PgBouncer (external dependency), custom pooling (unnecessary complexity)

7. **Timestamp Handling**
   - Decision: Use datetime.utcnow() for created_at/updated_at, store as TIMESTAMP
   - Rationale: Standard approach, timezone-aware, compatible with ISO 8601
   - Alternatives: Unix timestamps (less readable), timezone-aware datetime (more complex)

8. **API Versioning**
   - Decision: Use /api/v1 prefix for all endpoints
   - Rationale: Enables future API versions without breaking changes
   - Alternatives: No versioning (harder to evolve), header-based (less discoverable)

### Technology Choices

**FastAPI**: Selected for automatic OpenAPI docs, Pydantic validation, async support, and excellent developer experience.

**SQLModel**: Selected for combining SQLAlchemy ORM with Pydantic validation, reducing boilerplate and ensuring type safety across database and API layers.

**Neon PostgreSQL**: Selected for serverless architecture, instant branching for development, auto-scaling, and zero-downtime migrations.

**Uvicorn**: Selected as ASGI server for FastAPI, production-ready, supports async operations.

---

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions.

**Summary**:
- **Task Entity**: id (int, PK), title (str, required), description (str, optional), completed (bool, default false), user_id (int, required), created_at (datetime), updated_at (datetime)

### API Contracts

See [contracts/openapi.yaml](./contracts/openapi.yaml) for complete OpenAPI 3.0 specification.

**Endpoints**:
1. `POST /api/v1/tasks` - Create task (201 Created)
2. `GET /api/v1/tasks` - List all tasks (200 OK)
3. `GET /api/v1/tasks/{task_id}` - Get task by ID (200 OK, 404 Not Found)
4. `PUT /api/v1/tasks/{task_id}` - Update task (200 OK, 404 Not Found)
5. `PATCH /api/v1/tasks/{task_id}` - Partial update (200 OK, 404 Not Found)
6. `DELETE /api/v1/tasks/{task_id}` - Delete task (204 No Content, 404 Not Found)

### Implementation Approach

**Incremental Build Strategy**:

1. **Foundation Layer** (Tasks 1-3):
   - Set up project structure and dependencies
   - Configure database connection with environment variables
   - Create SQLModel Task model with all fields

2. **Core CRUD Layer** (Tasks 4-6):
   - Implement POST /api/v1/tasks (create)
   - Implement GET /api/v1/tasks (list all)
   - Implement GET /api/v1/tasks/{task_id} (get one)

3. **Update Layer** (Tasks 7-8):
   - Implement PUT /api/v1/tasks/{task_id} (full update)
   - Implement PATCH /api/v1/tasks/{task_id} (partial update)

4. **Delete Layer** (Task 9):
   - Implement DELETE /api/v1/tasks/{task_id}

5. **Validation & Error Handling** (Tasks 10-11):
   - Add comprehensive request validation
   - Implement consistent error responses

6. **CORS & Documentation** (Task 12):
   - Configure CORS for frontend communication
   - Verify OpenAPI docs at /docs

**Validation Strategy**: Each layer is validated before proceeding:
- Foundation: Verify database connection and model creation
- Core CRUD: Test create and retrieve operations via /docs
- Update: Test PUT and PATCH operations
- Delete: Test DELETE operation and verify removal
- Validation: Test error cases (missing fields, invalid IDs)
- CORS: Test from frontend origin

### Testing Strategy

**Manual API Verification**:
- Use FastAPI auto-generated docs at http://localhost:8000/docs
- Test each endpoint with valid and invalid inputs
- Verify HTTP status codes match specification
- Verify response JSON structure is consistent
- Test database persistence by restarting server

**Test Scenarios**:
1. Create task → verify 201 response with ID and timestamps
2. List tasks → verify 200 response with array
3. Get task by ID → verify 200 response with task details
4. Update task → verify 200 response with updated data
5. Partial update (toggle completed) → verify 200 response
6. Delete task → verify 204 response
7. Get deleted task → verify 404 response
8. Create task with missing title → verify 400 response with validation error
9. Get non-existent task → verify 404 response
10. Database restart → verify tasks persist

### Quickstart

See [quickstart.md](./quickstart.md) for complete setup and usage instructions.

**Quick Setup**:
```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add DATABASE_URL

# 3. Run server
uvicorn main:app --reload

# 4. Access API docs
# Open http://localhost:8000/docs
```

---

## Phase 2: Task Breakdown

Task breakdown will be generated by `/sp.tasks` command after plan approval.

**Expected Task Categories**:
- Setup tasks (project structure, dependencies, configuration)
- Database tasks (models, connection, session management)
- API endpoint tasks (one per endpoint)
- Validation tasks (request validation, error handling)
- Integration tasks (CORS, documentation verification)

---

## Risks & Mitigations

### Risk 1: Database Connection Failures
**Impact**: API becomes unavailable
**Mitigation**: Use pool_pre_ping=True to verify connections, implement graceful error handling with 500 responses

### Risk 2: Invalid user_id Values
**Impact**: Data integrity issues
**Mitigation**: Pydantic validation ensures user_id is positive integer, database constraint prevents null values

### Risk 3: Missing Environment Variables
**Impact**: Application fails to start
**Mitigation**: Use Pydantic Settings with validation, fail fast on startup with clear error message

### Risk 4: Neon Connection Limits
**Impact**: Connection pool exhaustion
**Mitigation**: Configure appropriate pool_size and max_overflow, use connection pooling best practices

---

## Future Considerations

**Authentication Integration** (Next Phase):
- Add JWT token verification middleware
- Filter tasks by authenticated user_id
- Add user table and foreign key constraint
- Implement signup/signin endpoints

**Performance Optimization** (Future):
- Add pagination for task listing
- Implement caching for frequently accessed tasks
- Add database indexes on user_id

**Feature Enhancements** (Future):
- Task filtering and sorting
- Task search functionality
- Task categories and tags
- Task due dates and priorities
