# Task Breakdown: Backend JWT Authentication & API Security

**Feature**: Backend JWT Authentication & API Security
**Branch**: `002-backend-jwt-auth`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

This task breakdown organizes implementation by user story priority, enabling independent development and testing of each feature increment. Each user story phase is a complete, testable slice of functionality.

**User Stories**:
- **US1 (P1)**: Secure API Access with JWT Tokens - Foundation of security model
- **US2 (P2)**: Automatic User Profile Provisioning - Lazy user creation from JWT
- **US3 (P3)**: Strict Task Data Isolation - User-scoped queries and access control

**Implementation Strategy**: MVP-first approach. US1 provides the authentication foundation, US2 adds user management, US3 enforces data isolation. Each story is independently testable.

---

## Phase 1: Setup & Project Initialization

**Goal**: Establish project structure, dependencies, and configuration foundation.

**Tasks**:

- [ ] T001 Create backend project structure per plan.md (backend/app/ with subdirectories: models/, middleware/, dependencies/, routers/, schemas/)
- [ ] T002 [P] Create requirements.txt with dependencies: fastapi>=0.104.0, sqlmodel>=0.0.14, python-jose[cryptography]>=3.3.0, psycopg2-binary>=2.9.9, python-dotenv>=1.0.0, uvicorn[standard]>=0.24.0, alembic>=1.12.0
- [ ] T003 [P] Create .env.example documenting required environment variables: DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, HOST, PORT
- [ ] T004 [P] Create .gitignore with entries: .env, __pycache__/, *.pyc, .pytest_cache/, alembic/versions/*.pyc
- [ ] T005 Initialize Alembic for database migrations in backend/ directory: alembic init alembic
- [ ] T006 [P] Create backend/app/__init__.py (empty file for package initialization)
- [ ] T007 [P] Create backend/app/models/__init__.py (empty file for package initialization)
- [ ] T008 [P] Create backend/app/middleware/__init__.py (empty file for package initialization)
- [ ] T009 [P] Create backend/app/dependencies/__init__.py (empty file for package initialization)
- [ ] T010 [P] Create backend/app/routers/__init__.py (empty file for package initialization)
- [ ] T011 [P] Create backend/app/schemas/__init__.py (empty file for package initialization)

---

## Phase 2: Foundational Infrastructure

**Goal**: Set up core application infrastructure required by all user stories.

**Blocking Prerequisites**: Must complete before any user story implementation.

**Tasks**:

- [ ] T012 Implement config module in backend/app/config.py to load environment variables (JWT_SECRET, JWT_ALGORITHM, DATABASE_URL) using python-dotenv with validation that JWT_SECRET is set
- [ ] T013 Implement database connection in backend/app/database.py with SQLModel engine, session factory, and get_session dependency for Neon PostgreSQL
- [ ] T014 Create FastAPI app initialization in backend/app/main.py with CORS middleware, app metadata (title, version), and placeholder for auth middleware registration
- [ ] T015 Configure Alembic env.py to use SQLModel metadata and DATABASE_URL from config for migrations

---

## Phase 3: User Story 1 - Secure API Access with JWT Tokens (P1)

**Story Goal**: Implement JWT authentication middleware that validates tokens on every request, extracts user identity, and rejects unauthorized requests with HTTP 401.

**Why P1**: Foundation of security model. Without JWT enforcement, all other security measures are meaningless.

**Independent Test Criteria**:
- ✅ Request without Authorization header returns 401 with "Authentication required"
- ✅ Request with invalid JWT returns 401 with "Invalid or expired token"
- ✅ Request with expired JWT returns 401 with "Token expired"
- ✅ Request with valid JWT succeeds and extracts user identity from "sub" claim
- ✅ Authentication failures are logged for security monitoring

**Tasks**:

- [X] T016 [US1] Implement JWT verification utility in backend/app/middleware/auth.py: decode_jwt() function using python-jose to validate token signature, expiration, and extract claims (sub, email, name)
- [X] T017 [US1] Implement authentication middleware in backend/app/middleware/auth.py: auth_middleware() that extracts JWT from Authorization header, validates token, and stores user info in request.state
- [X] T018 [US1] Implement error handling in auth middleware for missing token (401 "Authentication required"), invalid token (401 "Invalid or expired token"), and missing "sub" claim (401 "Invalid token format")
- [X] T019 [US1] Implement authentication failure logging in backend/app/middleware/auth.py using Python logging module with structured format (timestamp, error reason, IP address)
- [X] T020 [US1] Register auth middleware in backend/app/main.py using @app.middleware("http") decorator
- [X] T021 [US1] Implement get_current_user dependency in backend/app/dependencies/auth.py that retrieves user info from request.state and raises HTTPException(401) if not found
- [X] T022 [US1] Create health check endpoint GET /health in backend/app/main.py that bypasses authentication (for monitoring)

**Manual Testing** (via FastAPI /docs):
- Test request without Authorization header → expect 401
- Test request with invalid token → expect 401
- Test request with expired token → expect 401
- Test request with valid token → expect success (use any endpoint)
- Verify authentication failures are logged

---

## Phase 4: User Story 2 - Automatic User Profile Provisioning (P2)

**Story Goal**: Automatically create user records in the database on first authentication using data from JWT tokens, handling race conditions gracefully.

**Why P2**: Enables future frontend features without backend modifications. Establishes user identity foundation.

**Independent Test Criteria**:
- ✅ First-time user authentication creates user record in database with data from JWT (id, email, name)
- ✅ Subsequent authentications reuse existing user record (no duplicates)
- ✅ Race conditions handled gracefully (concurrent requests for new user create only one record)
- ✅ User provisioning succeeds even with minimal JWT data (only "sub" claim)

**Tasks**:

- [X] T023 [US2] Create User SQLModel in backend/app/models/user.py with fields: id (str, PK), email (str, UNIQUE), name (Optional[str]), avatar_url (Optional[str]), created_at (datetime), updated_at (datetime)
- [X] T024 [US2] Create User response schema in backend/app/schemas/user.py (Pydantic model) for API responses with same fields as User model
- [X] T025 [US2] Create Alembic migration for users table in backend/alembic/versions/: CREATE TABLE users with all fields, PRIMARY KEY on id, UNIQUE INDEX on email
- [X] T026 [US2] Apply users table migration: alembic upgrade head
- [X] T027 [US2] Implement get_or_create_user() function in backend/app/middleware/auth.py that attempts to fetch user by id, creates if not found, handles IntegrityError for race conditions
- [X] T028 [US2] Integrate user provisioning into auth middleware: call get_or_create_user() after JWT validation and store User object in request.state.user
- [X] T029 [US2] Update get_current_user dependency in backend/app/dependencies/auth.py to return User object (type-safe) instead of dict

**Manual Testing** (via FastAPI /docs):
- Authenticate with new user's JWT token → verify user record created in database
- Authenticate again with same token → verify no duplicate user created
- Check database: SELECT * FROM users WHERE id = '<user_id_from_jwt>'
- Test with JWT containing only "sub" claim → verify user created with minimal data

---

## Phase 5: User Story 3 - Strict Task Data Isolation (P3)

**Story Goal**: Enforce user isolation by filtering all task queries by authenticated user ID, preventing cross-user data access.

**Why P3**: Prevents cross-user data access vulnerabilities. Essential for multi-user applications.

**Independent Test Criteria**:
- ✅ User A cannot access User B's tasks (returns 404, not 403)
- ✅ GET /tasks returns only authenticated user's tasks
- ✅ POST /tasks creates task with authenticated user's ID
- ✅ PUT /tasks/{id} only updates authenticated user's tasks
- ✅ DELETE /tasks/{id} only deletes authenticated user's tasks

**Tasks**:

- [X] T030 [US3] Update Task SQLModel in backend/app/models/task.py to add user_id field: user_id (str, FK to users.id, NOT NULL, indexed)
- [X] T031 [US3] Create Alembic migration for adding user_id to tasks table in backend/alembic/versions/: ALTER TABLE tasks ADD COLUMN user_id, ADD FOREIGN KEY, CREATE INDEX on user_id, CREATE COMPOSITE INDEX on (id, user_id)
- [X] T032 [US3] Apply tasks user_id migration: alembic upgrade head
- [X] T033 [P] [US3] Create Task request schemas in backend/app/schemas/task.py: TaskCreate (title, description, priority, due_date), TaskUpdate (all fields optional)
- [X] T034 [P] [US3] Create Task response schema in backend/app/schemas/task.py with all fields including user_id
- [X] T035 [US3] Implement GET /tasks endpoint in backend/app/routers/tasks.py with user filtering: SELECT * FROM tasks WHERE user_id = current_user.id, with optional query params (completed, priority)
- [X] T036 [US3] Implement POST /tasks endpoint in backend/app/routers/tasks.py that creates task with user_id = current_user.id, validates request with TaskCreate schema, returns 201 with Location header
- [X] T037 [US3] Implement GET /tasks/{task_id} endpoint in backend/app/routers/tasks.py with user validation: SELECT * FROM tasks WHERE id = task_id AND user_id = current_user.id, returns 404 if not found
- [X] T038 [US3] Implement PUT /tasks/{task_id} endpoint in backend/app/routers/tasks.py with user validation, validates request with TaskUpdate schema, updates only if owned by user, returns 404 if not found
- [X] T039 [US3] Implement DELETE /tasks/{task_id} endpoint in backend/app/routers/tasks.py with user validation, deletes only if owned by user, returns 204 on success, 404 if not found
- [X] T040 [US3] Register task router in backend/app/main.py: app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
- [X] T041 [US3] Add structured error responses to all task endpoints: HTTPException with detail and code fields (e.g., {"detail": "Task not found", "code": "TASK_NOT_FOUND"})

**Manual Testing** (via FastAPI /docs):
- Create tasks with User A's token → note task IDs
- Switch to User B's token → try to access User A's tasks → expect 404
- GET /tasks with User A → verify only User A's tasks returned
- GET /tasks with User B → verify only User B's tasks returned
- POST /tasks → verify task created with correct user_id
- PUT /tasks/{id} with wrong user → expect 404
- DELETE /tasks/{id} with wrong user → expect 404

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Finalize implementation with documentation, error handling improvements, and deployment readiness.

**Tasks**:

- [X] T042 [P] Create README.md in backend/ with setup instructions: environment setup, dependency installation, database migrations, server startup
- [X] T043 [P] Update .env.example with detailed comments explaining each environment variable and example values
- [X] T044 [P] Add global exception handler in backend/app/main.py for unhandled exceptions: return 500 with generic error message (no stack traces)
- [X] T045 [P] Verify all endpoints return consistent error format: {"detail": "message", "code": "ERROR_CODE"}
- [X] T046 Test complete authentication flow end-to-end: signup → signin → get JWT → make authenticated requests → verify user isolation
- [X] T047 Verify constitution compliance: check all security gates (JWT auth, user isolation, no hardcoded secrets, proper error codes)
- [X] T048 [P] Document API endpoints in README.md with example cURL commands for each endpoint

---

## Dependencies & Execution Order

### Story Completion Order

```
Setup (Phase 1) → Foundational (Phase 2) → US1 (Phase 3) → US2 (Phase 4) → US3 (Phase 5) → Polish (Phase 6)
```

**Critical Path**:
- Setup → Foundational → US1 (JWT middleware) → US2 (User provisioning) → US3 (Task isolation) → Polish

**Story Dependencies**:
- **US1** (P1): No dependencies (can start after Foundational)
- **US2** (P2): Depends on US1 (requires JWT middleware to extract user data)
- **US3** (P3): Depends on US2 (requires User model and provisioning)

### Parallel Execution Opportunities

**Within Setup Phase** (T002-T011 can run in parallel):
- T002, T003, T004, T006-T011 are independent file creation tasks

**Within US1 Phase**:
- T016, T019, T021 can be developed in parallel (different concerns)
- T017, T018 must be sequential (error handling depends on middleware)

**Within US2 Phase**:
- T023, T024 can be developed in parallel (model and schema)
- T025, T027 can be developed in parallel (migration and provisioning logic)

**Within US3 Phase**:
- T030, T033, T034 can be developed in parallel (model update and schemas)
- T035-T039 can be developed in parallel (different endpoints, no shared state)

**Within Polish Phase**:
- T042, T043, T045, T048 can be developed in parallel (documentation tasks)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: Complete through **US1 (Phase 3)** only.

**Rationale**: US1 provides the core authentication foundation. This allows testing JWT validation, error handling, and logging before adding user provisioning and task isolation complexity.

**MVP Deliverables**:
- JWT middleware validates tokens on every request
- Unauthenticated requests return 401
- Invalid/expired tokens return 401
- Authentication failures logged
- Health check endpoint for monitoring

**Post-MVP**: Add US2 (user provisioning) and US3 (task isolation) incrementally.

### Incremental Delivery

1. **Iteration 1** (US1): Authentication foundation
   - Deliverable: JWT validation working, all auth errors handled
   - Test: Manual testing via /docs with valid/invalid tokens

2. **Iteration 2** (US2): User management
   - Deliverable: Users auto-created from JWT, race conditions handled
   - Test: Database verification, concurrent request testing

3. **Iteration 3** (US3): Data isolation
   - Deliverable: All task endpoints user-scoped, cross-user access prevented
   - Test: Multi-user testing with different JWT tokens

4. **Iteration 4** (Polish): Production readiness
   - Deliverable: Documentation, error handling, constitution compliance
   - Test: End-to-end flow, security audit

### Agent Coordination

**Database Agent** (T023-T026, T030-T032):
- Create User and Task models
- Generate and apply migrations
- Verify schema and indexes

**Auth Agent** (T016-T022, T027-T029):
- Implement JWT middleware
- Implement user provisioning
- Implement authentication dependencies
- Add security logging

**Backend Agent** (T012-T015, T033-T041):
- Implement config and database setup
- Create task endpoints with user filtering
- Add structured error responses
- Register routers

**Manual Testing** (T046-T047):
- End-to-end authentication flow
- Constitution compliance verification
- Cross-user access testing

---

## Task Summary

**Total Tasks**: 48

**Tasks by Phase**:
- Phase 1 (Setup): 11 tasks
- Phase 2 (Foundational): 4 tasks
- Phase 3 (US1): 7 tasks
- Phase 4 (US2): 7 tasks
- Phase 5 (US3): 12 tasks
- Phase 6 (Polish): 7 tasks

**Tasks by User Story**:
- US1 (P1): 7 tasks
- US2 (P2): 7 tasks
- US3 (P3): 12 tasks
- Infrastructure: 15 tasks
- Polish: 7 tasks

**Parallel Opportunities**: 18 tasks marked with [P] can be executed in parallel within their phase

**Independent Test Criteria**: Each user story phase has clear acceptance criteria for independent testing

---

## Validation Checklist

Before marking this feature complete, verify:

- [ ] All 48 tasks completed and checked off
- [ ] All user story acceptance criteria met (see spec.md)
- [ ] Constitution compliance verified (all security gates passed)
- [ ] Manual testing completed for all user stories
- [ ] Documentation complete (README.md, .env.example)
- [ ] No hardcoded secrets in codebase
- [ ] All endpoints require JWT authentication (except /health)
- [ ] User isolation enforced (cross-user access returns 404)
- [ ] Authentication failures logged
- [ ] Database migrations applied successfully
- [ ] FastAPI /docs accessible and functional

---

## Notes

- **Tests**: This feature uses manual testing via FastAPI /docs. Automated tests (pytest) are out of scope for MVP but can be added later.
- **Performance**: JWT validation adds ~5-10ms overhead per request (acceptable per spec).
- **Security**: All authentication failures are logged for security monitoring.
- **Scalability**: Database indexes on user_id ensure fast user-scoped queries.
- **Race Conditions**: User provisioning uses database UNIQUE constraint + exception handling for idempotency.

**Next Steps**: Execute tasks in order, starting with Phase 1 (Setup). Use specialized agents for each phase as indicated in Agent Coordination section.
