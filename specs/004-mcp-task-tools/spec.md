# Feature Specification: MCP Server & Task Tools for AI Todo Chatbot

**Feature Branch**: `004-mcp-task-tools`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Phase III – Spec 4: MCP Server & Task Tools for AI Todo Chatbot"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Agent Retrieves User's Tasks (Priority: P1)

As an AI agent, I need to retrieve a user's task list so I can provide context-aware responses about their todos.

**Why this priority**: This is the foundation for all AI interactions - the agent must be able to see what tasks exist before it can help manage them. Without this, no other task operations are meaningful.

**Independent Test**: Can be fully tested by calling the list_tasks tool with a valid user_id and verifying it returns only that user's tasks in the correct format.

**Acceptance Scenarios**:

1. **Given** a user has 3 tasks in the database, **When** the AI agent calls list_tasks with that user_id, **Then** the tool returns all 3 tasks with complete details (id, title, description, completed status, timestamps)
2. **Given** a user has no tasks, **When** the AI agent calls list_tasks, **Then** the tool returns an empty list with success=true
3. **Given** User A has 5 tasks and User B has 3 tasks, **When** the AI agent calls list_tasks with User A's user_id, **Then** only User A's 5 tasks are returned (strict isolation)

---

### User Story 2 - AI Agent Creates New Task (Priority: P1)

As an AI agent, I need to create new tasks on behalf of users so I can help them capture todos through natural conversation.

**Why this priority**: Task creation is the primary value proposition of the AI chatbot - users should be able to say "remind me to buy milk" and have the agent create the task. This is essential for MVP.

**Independent Test**: Can be fully tested by calling the add_task tool with valid input (user_id, title, description) and verifying the task is persisted to the database with correct ownership.

**Acceptance Scenarios**:

1. **Given** a user wants to create a task, **When** the AI agent calls add_task with user_id, title="Buy milk", and description="Get 2% milk from store", **Then** a new task is created in the database with completed=false and the tool returns the task details including the generated task_id
2. **Given** a user wants to create a task with only a title, **When** the AI agent calls add_task with user_id and title="Call dentist" (no description), **Then** the task is created successfully with an empty description
3. **Given** invalid input (missing user_id or empty title), **When** the AI agent calls add_task, **Then** the tool returns success=false with a clear error message and error_code

---

### User Story 3 - AI Agent Marks Task Complete (Priority: P2)

As an AI agent, I need to mark tasks as complete or incomplete so users can update task status through conversation.

**Why this priority**: Completing tasks is a core workflow, but users can still get value from creating and viewing tasks without this. It's essential for a complete experience but not for initial testing.

**Independent Test**: Can be fully tested by calling the complete_task tool with a valid task_id and user_id, then verifying the task's completed status is updated in the database.

**Acceptance Scenarios**:

1. **Given** a user has an incomplete task, **When** the AI agent calls complete_task with the task_id, user_id, and completed=true, **Then** the task's completed status is updated to true and the tool returns the updated task details
2. **Given** a user has a completed task, **When** the AI agent calls complete_task with completed=false, **Then** the task is marked as incomplete
3. **Given** User A tries to complete User B's task, **When** the AI agent calls complete_task with User A's user_id and User B's task_id, **Then** the tool returns success=false with error_code="TASK_NOT_FOUND" (enforcing ownership)

---

### User Story 4 - AI Agent Updates Task Details (Priority: P3)

As an AI agent, I need to update task titles and descriptions so users can modify their todos through conversation.

**Why this priority**: While useful, users can work around this by deleting and recreating tasks. This is a quality-of-life feature that can be added after core CRUD operations work.

**Independent Test**: Can be fully tested by calling the update_task tool with a task_id, user_id, and new title/description, then verifying the changes are persisted.

**Acceptance Scenarios**:

1. **Given** a user wants to change a task title, **When** the AI agent calls update_task with task_id, user_id, and new_title="Buy organic milk", **Then** the task title is updated and the tool returns the updated task
2. **Given** a user wants to update only the description, **When** the AI agent calls update_task with task_id, user_id, and new_description (no new_title), **Then** only the description is updated
3. **Given** a task doesn't exist or belongs to another user, **When** the AI agent calls update_task, **Then** the tool returns success=false with error_code="TASK_NOT_FOUND"

---

### User Story 5 - AI Agent Deletes Task (Priority: P3)

As an AI agent, I need to delete tasks so users can remove completed or unwanted todos through conversation.

**Why this priority**: Deletion is important for long-term usability but not critical for initial testing. Users can accumulate tasks without immediate harm. This should be implemented after core operations are stable.

**Independent Test**: Can be fully tested by calling the delete_task tool with a valid task_id and user_id, then verifying the task is removed from the database.

**Acceptance Scenarios**:

1. **Given** a user wants to delete a task, **When** the AI agent calls delete_task with task_id and user_id, **Then** the task is permanently removed from the database and the tool returns success=true
2. **Given** a task doesn't exist, **When** the AI agent calls delete_task, **Then** the tool returns success=false with error_code="TASK_NOT_FOUND"
3. **Given** User A tries to delete User B's task, **When** the AI agent calls delete_task with User A's user_id and User B's task_id, **Then** the tool returns success=false with error_code="TASK_NOT_FOUND" (ownership enforced)

---

### Edge Cases

- What happens when the database connection fails during a tool call? Tool should return success=false with error_code="DATABASE_ERROR" and a user-friendly error message
- What happens when a user_id is invalid or missing? Tool should return success=false with error_code="INVALID_USER_ID"
- What happens when task title exceeds reasonable length (e.g., >500 characters)? Tool should return success=false with error_code="VALIDATION_ERROR" and specify the constraint
- What happens when the AI agent calls a tool with malformed input (wrong types)? Pydantic validation should catch this and return a clear validation error
- What happens when multiple AI agents try to update the same task simultaneously? Database transaction isolation should handle this - last write wins (acceptable for MVP)
- What happens when the MCP server restarts during operation? All state is in the database, so ongoing conversations should continue seamlessly after restart

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose an MCP server using the Official MCP SDK that can be discovered and called by AI agents
- **FR-002**: System MUST provide a list_tasks tool that returns all tasks for a given user_id, filtered by ownership
- **FR-003**: System MUST provide an add_task tool that creates new tasks with user_id, title, and optional description
- **FR-004**: System MUST provide a complete_task tool that toggles task completion status (true/false)
- **FR-005**: System MUST provide an update_task tool that modifies task title and/or description
- **FR-006**: System MUST provide a delete_task tool that permanently removes tasks from the database
- **FR-007**: All tools MUST validate user_id and enforce strict ownership - users can only access their own tasks
- **FR-008**: All tools MUST be stateless - no in-memory caching or session state between calls
- **FR-009**: All tools MUST persist data to PostgreSQL via SQLModel before returning success
- **FR-010**: All tools MUST use explicit Pydantic schemas for input validation and output structure
- **FR-011**: All tools MUST return structured responses with success boolean, data object, error message, and error_code
- **FR-012**: System MUST handle database errors gracefully and return appropriate error codes
- **FR-013**: System MUST validate all inputs (user_id, task_id, title length, etc.) before database operations
- **FR-014**: All database queries MUST include WHERE user_id = <authenticated_user_id> to enforce isolation
- **FR-015**: System MUST use the existing Task model from SQLModel (no schema duplication)

### Key Entities

- **Task**: Represents a todo item with id (integer), user_id (integer, foreign key), title (string, required), description (string, optional), completed (boolean, default false), created_at (timestamp), updated_at (timestamp)
- **MCP Tool**: Represents a callable function exposed by the MCP server with explicit input schema (Pydantic model), output schema (Pydantic model), and stateless implementation
- **Tool Response**: Standard response structure with success (boolean), data (optional dict), error (optional string), error_code (optional string)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: MCP server initializes successfully and registers all 5 tools (add_task, list_tasks, update_task, complete_task, delete_task) within 2 seconds of startup
- **SC-002**: AI agent can successfully call list_tasks and retrieve a user's complete task list in under 500ms for up to 100 tasks
- **SC-003**: AI agent can create a new task via add_task and the task appears in the database within 1 second
- **SC-004**: 100% of tool calls with valid inputs return success=true with correct data structure
- **SC-005**: 100% of tool calls with invalid inputs (wrong user_id, missing fields, etc.) return success=false with clear error_code and error message
- **SC-006**: User isolation is enforced - 0% of tool calls can access or modify tasks belonging to other users
- **SC-007**: MCP server can be restarted without data loss - all tasks remain accessible after restart
- **SC-008**: All tool input and output schemas are documented and validated by Pydantic (0 runtime type errors)
- **SC-009**: Database queries execute efficiently - list_tasks returns results in under 100ms for typical workloads (up to 50 tasks per user)
- **SC-010**: AI agent can perform a complete task lifecycle (create → list → update → complete → delete) successfully in under 5 seconds total

## Assumptions *(mandatory)*

- **A-001**: The user_id is provided by the calling context (AI agent) and is already authenticated/validated before reaching the MCP tools
- **A-002**: The existing Task model in SQLModel is sufficient and doesn't need modification for MCP integration
- **A-003**: The MCP server will run as part of the existing FastAPI backend (not a separate service)
- **A-004**: Database connection pooling is already configured for Neon Serverless PostgreSQL
- **A-005**: The AI agent (OpenAI Agents SDK) knows how to discover and call MCP tools via the standard MCP protocol
- **A-006**: Error handling follows the pattern: success=false, error="Human-readable message", error_code="MACHINE_READABLE_CODE"
- **A-007**: Task title has a reasonable maximum length of 500 characters (enforced by validation)
- **A-008**: Task description has a reasonable maximum length of 2000 characters (enforced by validation)
- **A-009**: The MCP server does not need authentication middleware - authentication is handled upstream and user_id is trusted
- **A-010**: Concurrent access to the same task by multiple agents is rare enough that last-write-wins is acceptable (no optimistic locking required for MVP)

## Dependencies *(mandatory)*

- **D-001**: Existing Task model in SQLModel (from Phase II backend implementation)
- **D-002**: Neon Serverless PostgreSQL database with tasks table already created
- **D-003**: Official MCP SDK for Python (must be installed via pip)
- **D-004**: SQLModel and Pydantic for ORM and validation
- **D-005**: Database connection configuration (DATABASE_URL environment variable)
- **D-006**: FastAPI backend infrastructure (if MCP server is integrated into existing backend)

## Constraints *(mandatory)*

- **C-001**: MUST use Official MCP SDK only - no custom MCP implementations or alternative protocols
- **C-002**: MUST use Python as the implementation language
- **C-003**: MUST use SQLModel for all database operations - no raw SQL or other ORMs
- **C-004**: MUST use Neon Serverless PostgreSQL - no other databases
- **C-005**: MUST be stateless - no in-memory state, caching, or session storage
- **C-006**: MUST enforce user_id ownership on every database query - no cross-user data access
- **C-007**: MUST use Pydantic models for all tool input and output schemas
- **C-008**: MUST follow the constitution's MCP Tool Standards (Principle VIII)
- **C-009**: MUST NOT bypass the tool layer - AI agent cannot access database directly
- **C-010**: MUST handle all errors gracefully without exposing internal implementation details

## Out of Scope *(mandatory)*

- **OS-001**: Authentication and authorization - user_id is assumed to be validated upstream
- **OS-002**: Rate limiting or throttling of tool calls
- **OS-003**: Audit logging of tool calls (may be added later)
- **OS-004**: Batch operations (e.g., delete multiple tasks at once)
- **OS-005**: Advanced filtering (e.g., list only completed tasks, search by keyword)
- **OS-006**: Task sorting or pagination (list_tasks returns all tasks unsorted)
- **OS-007**: Task sharing or collaboration features
- **OS-008**: Task categories, tags, or priorities
- **OS-009**: Task due dates or reminders
- **OS-010**: Undo/redo functionality for task operations
- **OS-011**: Optimistic locking or conflict resolution for concurrent updates
- **OS-012**: Performance optimization beyond basic indexing (user_id index assumed to exist)
- **OS-013**: Integration with external task management systems
- **OS-014**: Custom tool discovery or dynamic tool registration
- **OS-015**: Tool versioning or backward compatibility (MVP uses single version)
