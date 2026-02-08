---
description: "Task list for MCP Server & Task Tools implementation"
---

# Tasks: MCP Server & Task Tools for AI Todo Chatbot

**Input**: Design documents from `/specs/004-mcp-task-tools/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the specification, so test tasks are not included. Testing will be performed manually using quickstart.md guide.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` for Python FastAPI backend
- All MCP-related code in `backend/mcp/` module

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create MCP module structure and update dependencies

- [x] T001 Create backend/mcp/ directory with __init__.py
- [x] T002 Create backend/mcp/schemas/ directory with __init__.py
- [x] T003 Create backend/mcp/tools/ directory with __init__.py
- [x] T004 Add mcp>=1.0.0 to backend/requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schemas and MCP server initialization that MUST be complete before ANY user story tool can be implemented

**⚠️ CRITICAL**: No user story tool implementation can begin until this phase is complete

- [x] T005 [P] Implement ToolResponse base schema in backend/mcp/schemas/base.py with success, data, error, error_code fields
- [x] T006 [P] Implement ListTasksInput schema in backend/mcp/schemas/task_inputs.py with user_id, completed, priority fields
- [x] T007 [P] Implement AddTaskInput schema in backend/mcp/schemas/task_inputs.py with user_id, title, description, priority, due_date fields
- [x] T008 [P] Implement CompleteTaskInput schema in backend/mcp/schemas/task_inputs.py with user_id, task_id, completed fields
- [x] T009 [P] Implement UpdateTaskInput schema in backend/mcp/schemas/task_inputs.py with user_id, task_id, new_title, new_description fields and validator
- [x] T010 [P] Implement DeleteTaskInput schema in backend/mcp/schemas/task_inputs.py with user_id, task_id fields
- [x] T011 Initialize MCP server in backend/mcp/server.py using Official MCP SDK with server name "task-tools-server"

**Checkpoint**: Foundation ready - user story tool implementation can now begin in parallel

---

## Phase 3: User Story 1 - AI Agent Retrieves User's Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable AI agents to retrieve a user's task list with optional filtering by completion status and priority

**Independent Test**: Call list_tasks tool with a valid user_id and verify it returns only that user's tasks in the correct format (success=true, data with tasks array and count)

### Implementation for User Story 1

- [x] T012 [US1] Implement list_tasks tool in backend/mcp/tools/list_tasks.py with user isolation (filter by user_id), optional completed and priority filters, return ToolResponse with tasks array and count
- [x] T013 [US1] Register list_tasks tool in backend/mcp/server.py with @server.tool() decorator

**Checkpoint**: At this point, User Story 1 should be fully functional - AI agents can retrieve user tasks with proper isolation

---

## Phase 4: User Story 2 - AI Agent Creates New Task (Priority: P1) 🎯 MVP

**Goal**: Enable AI agents to create new tasks on behalf of users through natural conversation

**Independent Test**: Call add_task tool with valid input (user_id, title, description) and verify the task is persisted to the database with correct ownership and completed=false

### Implementation for User Story 2

- [x] T014 [US2] Implement add_task tool in backend/mcp/tools/add_task.py with input validation (title 1-500 chars, description max 2000 chars), user_id enforcement, database insert, return ToolResponse with created task
- [x] T015 [US2] Register add_task tool in backend/mcp/server.py with @server.tool() decorator

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - AI agents can create and retrieve tasks

---

## Phase 5: User Story 3 - AI Agent Marks Task Complete (Priority: P2)

**Goal**: Enable AI agents to mark tasks as complete or incomplete so users can update task status through conversation

**Independent Test**: Call complete_task tool with a valid task_id and user_id, then verify the task's completed status is updated in the database and updated_at timestamp is refreshed

### Implementation for User Story 3

- [x] T016 [US3] Implement complete_task tool in backend/mcp/tools/complete_task.py with ownership verification (user_id filter), update completed status and updated_at timestamp, return ToolResponse with updated task or TASK_NOT_FOUND error
- [x] T017 [US3] Register complete_task tool in backend/mcp/server.py with @server.tool() decorator

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - AI agents can create, retrieve, and complete tasks

---

## Phase 6: User Story 4 - AI Agent Updates Task Details (Priority: P3)

**Goal**: Enable AI agents to update task titles and descriptions so users can modify their todos through conversation

**Independent Test**: Call update_task tool with a task_id, user_id, and new title/description, then verify the changes are persisted and updated_at timestamp is refreshed

### Implementation for User Story 4

- [x] T018 [US4] Implement update_task tool in backend/mcp/tools/update_task.py with ownership verification, partial update support (title only, description only, or both), updated_at timestamp refresh, return ToolResponse with updated task or TASK_NOT_FOUND/VALIDATION_ERROR
- [x] T019 [US4] Register update_task tool in backend/mcp/server.py with @server.tool() decorator

**Checkpoint**: At this point, User Stories 1-4 should all work independently - AI agents can create, retrieve, complete, and update tasks

---

## Phase 7: User Story 5 - AI Agent Deletes Task (Priority: P3)

**Goal**: Enable AI agents to delete tasks so users can remove completed or unwanted todos through conversation

**Independent Test**: Call delete_task tool with a valid task_id and user_id, then verify the task is removed from the database and no longer appears in list_tasks results

### Implementation for User Story 5

- [x] T020 [US5] Implement delete_task tool in backend/mcp/tools/delete_task.py with ownership verification (user_id filter), permanent deletion from database, return ToolResponse with task_id and deleted=true or TASK_NOT_FOUND error
- [x] T021 [US5] Register delete_task tool in backend/mcp/server.py with @server.tool() decorator

**Checkpoint**: All user stories should now be independently functional - complete CRUD operations available to AI agents

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validation, testing, and documentation

- [x] T022 Verify all 5 tools are registered in backend/mcp/server.py and server initializes successfully
- [ ] T023 Test user isolation using quickstart.md guide - verify User A cannot access User B's tasks (all tools return TASK_NOT_FOUND for cross-user attempts) [REQUIRES DATABASE]
- [ ] T024 Test stateless architecture using quickstart.md guide - restart MCP server and verify all data persists (no in-memory state) [REQUIRES DATABASE]
- [x] T025 Verify all error codes are implemented correctly (INVALID_USER_ID, TASK_NOT_FOUND, VALIDATION_ERROR, DATABASE_ERROR, INTERNAL_ERROR)
- [ ] T026 Run performance benchmarks from quickstart.md - verify list_tasks <500ms, write operations <1 second [REQUIRES DATABASE]
- [x] T027 Verify all tools return structured ToolResponse with success, data, error, error_code fields

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P3 → P3)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tool implementation before registration
- Each story is independently testable after completion

### Parallel Opportunities

- All Setup tasks (T001-T004) can run in parallel
- All Foundational schema tasks (T005-T010) can run in parallel
- Once Foundational phase completes, all user stories (Phase 3-7) can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: Foundational Phase

```bash
# Launch all schema implementations together:
Task: "Implement ToolResponse base schema in backend/mcp/schemas/base.py"
Task: "Implement ListTasksInput schema in backend/mcp/schemas/task_inputs.py"
Task: "Implement AddTaskInput schema in backend/mcp/schemas/task_inputs.py"
Task: "Implement CompleteTaskInput schema in backend/mcp/schemas/task_inputs.py"
Task: "Implement UpdateTaskInput schema in backend/mcp/schemas/task_inputs.py"
Task: "Implement DeleteTaskInput schema in backend/mcp/schemas/task_inputs.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (list_tasks)
4. Complete Phase 4: User Story 2 (add_task)
5. **STOP and VALIDATE**: Test US1 and US2 independently using quickstart.md
6. Deploy/demo if ready - AI agents can now create and retrieve tasks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → AI agents can retrieve tasks
3. Add User Story 2 → Test independently → AI agents can create and retrieve tasks (MVP!)
4. Add User Story 3 → Test independently → AI agents can complete tasks
5. Add User Story 4 → Test independently → AI agents can update tasks
6. Add User Story 5 → Test independently → AI agents can delete tasks (Full CRUD!)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (list_tasks)
   - Developer B: User Story 2 (add_task)
   - Developer C: User Story 3 (complete_task)
   - Developer D: User Story 4 (update_task)
   - Developer E: User Story 5 (delete_task)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All tools must enforce user_id ownership on every database query
- All tools must be stateless (no in-memory caching or session state)
- All tools must return structured ToolResponse with success, data, error, error_code
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use quickstart.md for manual testing and validation
- Reuse existing Task model from backend/models/task.py (no modifications)
- Share database engine from backend/core/database.py (no separate connections)
