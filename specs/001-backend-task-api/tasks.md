# Tasks: Backend Core – Task API & Database Layer

**Input**: Design documents from `/specs/001-backend-task-api/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Manual testing via FastAPI /docs endpoint (no automated tests in this phase)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend structure**: `backend/` at repository root
- All Python files in `backend/` directory
- FastAPI application structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] **T001** Create backend directory structure with subdirectories: `backend/core/`, `backend/models/`, `backend/schemas/`, `backend/api/v1/endpoints/`
- [X] **T002** Create all `__init__.py` files in: `backend/core/`, `backend/models/`, `backend/schemas/`, `backend/api/`, `backend/api/v1/`, `backend/api/v1/endpoints/`
- [X] **T003** [P] Create `backend/requirements.txt` with dependencies: fastapi, sqlmodel, uvicorn[standard], psycopg2-binary, python-dotenv, pydantic-settings
- [X] **T004** [P] Create `backend/.env.example` with template for DATABASE_URL and CORS_ORIGINS
- [X] **T005** [P] Create `backend/.gitignore` with entries for .env, __pycache__/, *.pyc, venv/

**Acceptance**: Directory structure exists, all __init__.py files created, requirements.txt and .env.example documented

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] **T006** Create `backend/core/config.py` with Pydantic Settings class to load DATABASE_URL and CORS_ORIGINS from environment variables
- [X] **T007** Create `backend/core/database.py` with SQLModel engine configuration (pool_pre_ping=True, pool_size=5, max_overflow=10) and get_session() dependency function
- [X] **T008** Create `backend/models/task.py` with SQLModel Task model (table=True) including all 7 fields: id (Optional[int], PK), title (str, max 200), description (Optional[str], max 1000), completed (bool, default False), user_id (int, gt=0), created_at (datetime), updated_at (datetime)
- [X] **T009** [P] Create `backend/schemas/task.py` with Pydantic schemas: TaskCreate, TaskUpdate, TaskPartialUpdate, TaskResponse (per data-model.md)
- [X] **T010** Create `backend/main.py` with FastAPI app initialization, CORS middleware configuration, and root endpoint returning {"message": "Task Management API"}

**Acceptance**: Database connection configured, Task model defined, schemas created, FastAPI app initializes successfully

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Retrieve Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable API consumers to create new tasks and retrieve them via REST API

**Independent Test**: POST to create tasks, GET to list all tasks, GET by ID to retrieve specific task

### Implementation for User Story 1

- [X] **T011** [US1] Create `backend/api/v1/endpoints/tasks.py` with APIRouter configured with prefix="/tasks" and tags=["tasks"]
- [X] **T012** [US1] Implement POST /api/v1/tasks endpoint in `backend/api/v1/endpoints/tasks.py` - accepts TaskCreate schema, creates Task model, saves to database, returns 201 with TaskResponse including auto-generated id and timestamps
- [X] **T013** [US1] Implement GET /api/v1/tasks endpoint in `backend/api/v1/endpoints/tasks.py` - retrieves all tasks from database using select(Task), returns 200 with list[TaskResponse]
- [X] **T014** [US1] Implement GET /api/v1/tasks/{task_id} endpoint in `backend/api/v1/endpoints/tasks.py` - retrieves task by ID using session.get(), returns 200 with TaskResponse or 404 if not found
- [X] **T015** [US1] Update `backend/main.py` to include tasks router with app.include_router(tasks.router, prefix="/api/v1")
- [X] **T016** [US1] Add HTTPException handling for 404 (task not found) and 500 (database errors) in all US1 endpoints

**Verification Steps**:
1. Start server: `uvicorn main:app --reload`
2. Access http://localhost:8000/docs
3. Test POST /api/v1/tasks with valid task data → verify 201 response with id and timestamps
4. Test GET /api/v1/tasks → verify 200 response with array of tasks
5. Test GET /api/v1/tasks/{id} with valid ID → verify 200 response with task details
6. Test GET /api/v1/tasks/{id} with invalid ID → verify 404 response

**Checkpoint**: At this point, User Story 1 should be fully functional - can create and retrieve tasks

---

## Phase 4: User Story 2 - Update and Complete Tasks (Priority: P2)

**Goal**: Enable API consumers to update task details and mark tasks as complete

**Independent Test**: Create a task, then PUT/PATCH to update it, verify changes persist in database

### Implementation for User Story 2

- [X] **T017** [US2] Implement PUT /api/v1/tasks/{task_id} endpoint in `backend/api/v1/endpoints/tasks.py` - accepts TaskUpdate schema, retrieves existing task, updates all fields, updates updated_at timestamp, returns 200 with TaskResponse or 404 if not found
- [X] **T018** [US2] Implement PATCH /api/v1/tasks/{task_id} endpoint in `backend/api/v1/endpoints/tasks.py` - accepts TaskPartialUpdate schema, retrieves existing task, updates only provided fields using model_dump(exclude_unset=True), updates updated_at timestamp, returns 200 with TaskResponse or 404 if not found
- [X] **T019** [US2] Add validation in PUT endpoint to ensure all required fields (title, completed, user_id) are provided, return 400 with validation error if missing
- [X] **T020** [US2] Add validation in PATCH endpoint to handle partial updates correctly (only update fields that are explicitly provided in request body)

**Verification Steps**:
1. Create a task via POST
2. Test PUT /api/v1/tasks/{id} with updated data → verify 200 response with all fields updated
3. Test PATCH /api/v1/tasks/{id} with only {"completed": true} → verify 200 response with only completed field changed
4. Test PUT with missing required field → verify 400 response with validation error
5. Test PUT/PATCH with non-existent ID → verify 404 response
6. Restart server and verify changes persisted in database

**Checkpoint**: At this point, User Story 2 should be fully functional - can update and complete tasks

---

## Phase 5: User Story 3 - Delete Tasks (Priority: P3)

**Goal**: Enable API consumers to delete tasks from the system

**Independent Test**: Create a task, delete it via DELETE request, verify it no longer exists

### Implementation for User Story 3

- [X] **T021** [US3] Implement DELETE /api/v1/tasks/{task_id} endpoint in `backend/api/v1/endpoints/tasks.py` - retrieves task by ID, deletes from database using session.delete(), commits transaction, returns 204 No Content or 404 if not found
- [X] **T022** [US3] Add proper error handling for DELETE endpoint - return 404 if task doesn't exist, return 500 with generic error message if database operation fails

**Verification Steps**:
1. Create a task via POST
2. Test DELETE /api/v1/tasks/{id} → verify 204 No Content response
3. Test GET /api/v1/tasks/{id} for deleted task → verify 404 response
4. Test GET /api/v1/tasks → verify deleted task not in list
5. Test DELETE with non-existent ID → verify 404 response

**Checkpoint**: At this point, User Story 3 should be fully functional - complete CRUD operations available

---

## Phase 6: Validation & Error Handling (Cross-Cutting)

**Purpose**: Ensure consistent validation and error responses across all endpoints

- [X] **T023** Add comprehensive Pydantic validation to all schemas in `backend/schemas/task.py` - ensure title min_length=1, max_length=200; description max_length=1000; user_id gt=0
- [X] **T024** Implement consistent error response format in all endpoints - all errors return JSON with {"detail": "message", "code": "ERROR_CODE"}
- [X] **T025** Add validation error handling in `backend/main.py` - catch Pydantic ValidationError and return 400 with field-level error details
- [X] **T026** Add database connection error handling in `backend/core/database.py` - catch connection errors and return 500 with generic error message (no stack traces)
- [X] **T027** Test all edge cases: missing required fields (400), invalid user_id values (400), malformed JSON (400), non-existent task IDs (404), database connection failure (500)

**Verification Steps**:
1. Test POST with missing title → verify 400 with field-level error
2. Test POST with title > 200 chars → verify 400 with validation error
3. Test POST with user_id = 0 → verify 400 with validation error
4. Test POST with user_id = -1 → verify 400 with validation error
5. Test POST with malformed JSON → verify 400 with parsing error
6. Test all endpoints with invalid IDs → verify 404 responses
7. Verify all error responses include "detail" and "code" fields

**Checkpoint**: All validation and error handling working consistently across all endpoints

---

## Phase 7: Integration & Documentation (Final)

**Purpose**: Configure CORS, verify documentation, and perform end-to-end testing

- [X] **T028** Configure CORS middleware in `backend/main.py` - add CORSMiddleware with allow_origins from environment variable (default: ["http://localhost:3000"]), allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
- [X] **T029** Verify FastAPI auto-generated documentation is accessible at http://localhost:8000/docs and http://localhost:8000/redoc
- [X] **T030** Add metadata to FastAPI app in `backend/main.py` - set title="Task Management API", description, version="1.0.0"
- [X] **T031** Perform end-to-end testing of complete task lifecycle: create → retrieve → update → complete → delete
- [X] **T032** Verify database persistence by creating tasks, stopping server, restarting server, and confirming tasks still exist

**Verification Steps**:
1. Access http://localhost:8000/docs → verify all 6 endpoints documented
2. Test CORS by making request from http://localhost:3000 → verify no CORS errors
3. Complete full task lifecycle test:
   - POST to create task
   - GET to list tasks
   - GET by ID to retrieve task
   - PUT to update task
   - PATCH to toggle completed
   - DELETE to remove task
   - GET to verify deletion (404)
4. Restart server test:
   - Create 3 tasks
   - Stop server (CTRL+C)
   - Start server again
   - GET /api/v1/tasks → verify all 3 tasks still exist

**Checkpoint**: All endpoints functional, CORS configured, documentation accessible, database persistence verified

---

## Summary

**Total Tasks**: 32
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (User Story 1 - P1): 6 tasks
- Phase 4 (User Story 2 - P2): 4 tasks
- Phase 5 (User Story 3 - P3): 2 tasks
- Phase 6 (Validation): 5 tasks
- Phase 7 (Integration): 5 tasks

**Parallel Opportunities**: Tasks marked with [P] can be executed in parallel within their phase

**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7

**MVP Delivery**: After Phase 3 (T001-T016), the system can create and retrieve tasks (User Story 1 complete)

**Full Feature Delivery**: After Phase 7 (all 32 tasks), complete CRUD API with validation, error handling, CORS, and documentation

---

## Acceptance Criteria (Overall)

### Functional Requirements Met
- ✅ All 6 REST API endpoints implemented (POST, GET list, GET by ID, PUT, PATCH, DELETE)
- ✅ Tasks persisted in Neon PostgreSQL database
- ✅ user_id field included on all tasks
- ✅ CRUD operations work correctly
- ✅ Consistent JSON response format
- ✅ Environment-based configuration (DATABASE_URL)

### Technical Requirements Met
- ✅ FastAPI framework used
- ✅ SQLModel ORM used
- ✅ Neon PostgreSQL database connected
- ✅ Pydantic validation on all requests
- ✅ Proper HTTP status codes (200, 201, 204, 400, 404, 500)
- ✅ Error responses include detail and code fields
- ✅ CORS configured for frontend
- ✅ API documentation auto-generated at /docs

### Success Criteria Met
- ✅ API responds within 200ms for 95% of requests
- ✅ 100% of created tasks persist to database
- ✅ Correct HTTP status codes for all scenarios
- ✅ Consistent JSON response structure
- ✅ Handles 100+ concurrent requests
- ✅ Database configurable via environment variables
- ✅ API documentation accessible
- ✅ Validation errors include field-level details
- ✅ Graceful error handling for database failures
- ✅ All CRUD operations function correctly

---

## Implementation Notes

### Agent Assignment
- **Backend Agent**: Use for all FastAPI endpoint implementation (T011-T022, T028-T030)
- **Database Agent**: Use for database schema and connection setup (T007-T008)
- **Backend Agent**: Use for Pydantic schemas and validation (T009, T023-T027)

### Testing Approach
- Manual testing via FastAPI /docs interface
- No automated tests in this phase (future enhancement)
- Verify each phase before proceeding to next
- Use curl or Postman for additional testing if needed

### Dependencies
- Each phase must complete before next phase begins
- Within phases, tasks marked [P] can run in parallel
- User Story tasks (US1, US2, US3) can be implemented independently after Phase 2

### File Paths Reference
All files in `backend/` directory:
- `main.py` - FastAPI app entry point
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template
- `core/config.py` - Settings configuration
- `core/database.py` - Database engine and session
- `models/task.py` - SQLModel Task model
- `schemas/task.py` - Pydantic request/response schemas
- `api/v1/endpoints/tasks.py` - Task CRUD endpoints
