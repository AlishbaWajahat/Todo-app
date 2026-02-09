# Task Breakdown: Stateless Task Agent with MCP Tool Invocation

**Feature**: 005-stateless-task-agent | **Branch**: `005-stateless-task-agent` | **Date**: 2026-02-09

**Input**: Design artifacts from `/sp.plan` command
- [spec.md](spec.md) - Feature specification with 5 user stories
- [plan.md](plan.md) - Implementation plan with technical decisions
- [research.md](research.md) - Technical research and alternatives
- [data-model.md](data-model.md) - Conceptual entities
- [quickstart.md](quickstart.md) - Testing scenarios
- [contracts/agent_endpoint.json](contracts/agent_endpoint.json) - API contract

**Reference**: [reference/agent.py](../../reference/agent.py) - Gemini configuration pattern

---

## Phase 1: Setup and Infrastructure

**Goal**: Create module structure and install dependencies

- [x] [T001] [P1] [Setup] Create backend/agent/ module directory with __init__.py
- [x] [T002] [P1] [Setup] Add openai-agents>=0.8.0 to backend/requirements.txt
- [x] [T003] [P1] [Setup] Add openai>=1.0.0 to backend/requirements.txt (for AsyncOpenAI client)
- [x] [T004] [P1] [Setup] Install dependencies: `pip install -r backend/requirements.txt`
- [x] [T005] [P1] [Setup] Add GEMINI_API_KEY to backend/.env file
- [x] [T006] [P1] [Setup] Add OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/ to backend/core/config.py

**Acceptance**: Module structure exists, dependencies installed, environment configured

---

## Phase 2: Foundational - Agent Configuration with Gemini

**Goal**: Implement base agent initialization using OpenAI Agent SDK with Gemini routing

**Blocking**: Phase 1 must complete first

- [x] [T007] [P1] [Foundation] Create backend/agent/agent.py with AsyncOpenAI client initialization
  - Import: `from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel`
  - Create AsyncOpenAI client with api_key=GEMINI_API_KEY, base_url from config
  - Create OpenAIChatCompletionsModel with model="gemini-2.5-flash"
  - Create RunConfig with model and tracing_disabled=True
  - Reference: reference/agent.py lines 15-25

- [x] [T008] [P1] [Foundation] Create backend/agent/intent_parser.py with rule-based classification
  - Define Intent enum: CREATE, LIST, COMPLETE, UPDATE, DELETE, UNKNOWN
  - Implement parse_intent(message: str) -> IntentClassification function
  - Add keyword patterns for each intent (create/add/new, list/show, done/complete, change/update, delete/remove)
  - Return IntentClassification with operation_type, confidence, extracted_parameters, classification_method
  - Reference: research.md Decision 2 (lines 29-57)

- [x] [T009] [P1] [Foundation] Create backend/agent/response_formatter.py with natural language formatting
  - Implement format_success_response(tool_name: str, tool_output: dict) -> str
  - Implement format_error_response(error_code: str, error_message: str) -> str
  - Add response templates for each tool (CREATE: "Task created: {title}", LIST: "You have {count} tasks: {list}")
  - Reference: data-model.md lines 190-203

- [x] [T010] [P1] [Foundation] Implement MCP tool imports in backend/agent/agent.py
  - Import all 5 MCP tools: list_tasks, add_task, complete_task, update_task, delete_task
  - Import path: `from mcp.tools.list_tasks import list_tasks` (and similar for others)
  - Reference: research.md Decision 5 (lines 105-131)

**Acceptance**: Agent module can initialize with Gemini, parse basic intents, format responses

---

## Phase 3: User Story 1 - Create Task via Natural Language (P1 - MVP)

**Goal**: Implement task creation through natural language

**Blocking**: Phase 2 must complete first

- [x] [T011] [P1] [US1] Implement CREATE intent pattern matching in intent_parser.py
  - Add patterns: "create", "add", "new task", "remind me to"
  - Extract title from message (text after action verb or quoted text)
  - Extract optional description, priority (high/medium/low), due_date (temporal expressions)
  - Return IntentClassification with operation_type=CREATE, extracted parameters
  - Test: "Create a task to buy groceries" → title="Buy groceries"

- [x] [T012] [P1] [US1] Implement add_task tool invocation in agent.py
  - Create invoke_add_task(user_id: str, params: dict) -> ToolResponse function
  - Call add_task MCP tool with user_id, title, description, priority, due_date
  - Handle ToolResponse (success or error)
  - Reference: plan.md lines 88-110

- [x] [T013] [P1] [US1] Implement CREATE response formatting in response_formatter.py
  - Add format_create_response(task: dict) -> str function
  - Template: "Task created: {title}" for simple cases
  - Template: "Task created: {title} (priority: {priority}, due: {due_date})" for detailed cases
  - Reference: quickstart.md lines 62-73

- [x] [T014] [P1] [US1] Create FastAPI endpoint POST /api/agent/chat in backend/api/agent_routes.py
  - Define AgentRequest schema: user_id (str), message (str, max 1000 chars)
  - Define AgentResponse schema: response (str), metadata (optional dict)
  - Implement async endpoint that calls agent.process_request(user_id, message)
  - Return AgentResponse with natural language response and metadata
  - Reference: contracts/agent_endpoint.json lines 14-67

- [x] [T015] [P1] [US1] Implement main agent request handler in agent.py
  - Create async process_request(user_id: str, message: str) -> AgentResponse function
  - Flow: parse_intent → invoke_tool → format_response
  - Track execution_time_ms for metadata
  - Handle all exceptions and return user-friendly error messages
  - Reference: plan.md lines 88-110

- [x] [T016] [P1] [US1] Test US1 acceptance scenarios from spec.md
  - Test: "Create a task to buy groceries" → Task created with title="Buy groceries"
  - Test: "Add a high priority task to call dentist by Friday" → Task with priority and due_date
  - Test: "Remind me to finish the report with detailed analysis" → Task with description
  - Test: Ambiguous message "do something" → Clarification or minimal task creation
  - Reference: spec.md lines 20-23

**Acceptance**: Agent can create tasks from natural language, endpoint returns natural language responses

---

## Phase 4: User Story 2 - List Tasks via Natural Language (P2)

**Goal**: Implement task listing through natural language

**Blocking**: Phase 3 must complete first (need working agent infrastructure)

- [x] [T017] [P2] [US2] Implement LIST intent pattern matching in intent_parser.py
  - Add patterns: "show", "list", "what are my", "display"
  - Extract optional filters: completed (boolean), priority (string)
  - Parse filter phrases: "tasks left" → completed=false, "high priority" → priority="high"
  - Return IntentClassification with operation_type=LIST, extracted filters
  - Test: "Show me my tasks" → no filters, "What tasks do I have left?" → completed=false

- [x] [T018] [P2] [US2] Implement list_tasks tool invocation in agent.py
  - Create invoke_list_tasks(user_id: str, params: dict) -> ToolResponse function
  - Call list_tasks MCP tool with user_id, completed filter, priority filter
  - Handle ToolResponse with tasks array
  - Reference: plan.md lines 88-110

- [x] [T019] [P2] [US2] Implement LIST response formatting in response_formatter.py
  - Add format_list_response(tasks: list) -> str function
  - Template: "You have {count} tasks: 1) {title1} 2) {title2} ..." (max 10 tasks)
  - Template: "You have no tasks" when list is empty
  - Include completion status indicators if relevant
  - Reference: quickstart.md lines 114-124

- [x] [T020] [P2] [US2] Test US2 acceptance scenarios from spec.md
  - Test: User with 3 tasks → "Show me my tasks" → Formatted list of all 3
  - Test: User with mixed tasks → "What tasks do I have left?" → Only incomplete tasks
  - Test: User with priorities → "Show me high priority tasks" → Filtered by priority
  - Test: User with no tasks → "List my tasks" → "You have no tasks"
  - Reference: spec.md lines 37-40

**Acceptance**: Agent can list tasks with optional filters, responses are concise and readable

---

## Phase 5: User Story 3 - Mark Task Complete via Natural Language (P3)

**Goal**: Implement task completion through natural language

**Blocking**: Phase 4 must complete first (need task listing for verification)

- [x] [T021] [P3] [US3] Implement COMPLETE intent pattern matching in intent_parser.py
  - Add patterns: "done", "finished", "complete", "mark as"
  - Extract task identifier: task_id (number) or task_title (string for fuzzy match)
  - Extract completion status: completed=true (default) or completed=false (for undo)
  - Return IntentClassification with operation_type=COMPLETE, task identifier, completed status
  - Test: "Mark 'Buy milk' as done" → task_title="Buy milk", completed=true

- [x] [T022] [P3] [US3] Implement task identification logic in agent.py
  - Create identify_task(user_id: str, task_id: int | None, task_title: str | None) -> int function
  - If task_id provided, return it directly
  - If task_title provided, call list_tasks and fuzzy match title (70% similarity threshold)
  - Return task_id or raise TASK_NOT_FOUND error
  - Reference: spec.md lines 155 (assumption 9)

- [x] [T023] [P3] [US3] Implement complete_task tool invocation in agent.py
  - Create invoke_complete_task(user_id: str, params: dict) -> ToolResponse function
  - Call identify_task to resolve task_id
  - Call complete_task MCP tool with user_id, task_id, completed status
  - Handle ToolResponse and TASK_NOT_FOUND errors
  - Reference: plan.md lines 88-110

- [x] [T024] [P3] [US3] Implement COMPLETE response formatting in response_formatter.py
  - Add format_complete_response(task: dict, completed: bool) -> str function
  - Template: "Marked '{title}' as done" or "Marked '{title}' as not done"
  - Reference: quickstart.md lines 163-174

- [x] [T025] [P3] [US3] Test US3 acceptance scenarios from spec.md
  - Test: "Mark 'Buy milk' as done" → Task identified by title, marked complete
  - Test: "Complete task 5" → Task identified by ID, marked complete
  - Test: Ambiguous reference with multiple matches → Clarification or most recent match
  - Test: "Undo completion of task 3" → Task marked as not complete
  - Reference: spec.md lines 54-57

**Acceptance**: Agent can complete tasks by title or ID, handles ambiguous references gracefully

---

## Phase 6: User Story 4 - Update Task Details via Natural Language (P4)

**Goal**: Implement task updates through natural language

**Blocking**: Phase 5 must complete first (reuses task identification logic)

- [x] [T026] [P4] [US4] Implement UPDATE intent pattern matching in intent_parser.py
  - Add patterns: "change", "update", "modify", "rename"
  - Extract task identifier: task_id or task_title
  - Extract new values: new_title, new_description
  - Parse update phrases: "Change X to Y" → old_title=X, new_title=Y
  - Return IntentClassification with operation_type=UPDATE, task identifier, new values
  - Test: "Change 'Buy milk' to 'Buy organic milk'" → task_title="Buy milk", new_title="Buy organic milk"

- [x] [T027] [P4] [US4] Implement update_task tool invocation in agent.py
  - Create invoke_update_task(user_id: str, params: dict) -> ToolResponse function
  - Call identify_task to resolve task_id
  - Validate at least one of new_title or new_description is provided
  - Call update_task MCP tool with user_id, task_id, new_title, new_description
  - Handle ToolResponse and validation errors
  - Reference: plan.md lines 88-110

- [x] [T028] [P4] [US4] Implement UPDATE response formatting in response_formatter.py
  - Add format_update_response(old_task: dict, new_task: dict) -> str function
  - Template: "Updated '{old_title}' to '{new_title}'" for title changes
  - Template: "Updated task {id} description" for description changes
  - Reference: quickstart.md lines 212-222

- [x] [T029] [P4] [US4] Test US4 acceptance scenarios from spec.md
  - Test: "Change 'Buy milk' to 'Buy organic milk'" → Title updated
  - Test: "Update task 3 description to include store location" → Description updated
  - Test: "Rename task 5 to 'Call dentist tomorrow'" → Title updated by ID
  - Reference: spec.md lines 71-73

**Acceptance**: Agent can update task title and description, validates input parameters

---

## Phase 7: User Story 5 - Delete Task via Natural Language (P5)

**Goal**: Implement task deletion through natural language

**Blocking**: Phase 6 must complete first (reuses task identification logic)

- [x] [T030] [P5] [US5] Implement DELETE intent pattern matching in intent_parser.py
  - Add patterns: "delete", "remove", "get rid of"
  - Extract task identifier: task_id or task_title
  - Return IntentClassification with operation_type=DELETE, task identifier
  - Test: "Delete 'Old task'" → task_title="Old task"

- [x] [T031] [P5] [US5] Implement delete_task tool invocation in agent.py
  - Create invoke_delete_task(user_id: str, params: dict) -> ToolResponse function
  - Call identify_task to resolve task_id
  - Call delete_task MCP tool with user_id, task_id
  - Handle ToolResponse and TASK_NOT_FOUND errors
  - Reference: plan.md lines 88-110

- [x] [T032] [P5] [US5] Implement DELETE response formatting in response_formatter.py
  - Add format_delete_response(task: dict) -> str function
  - Template: "Deleted task '{title}'"
  - Reference: quickstart.md lines 260-268

- [x] [T033] [P5] [US5] Test US5 acceptance scenarios from spec.md
  - Test: "Delete 'Old task'" → Task identified by title, deleted
  - Test: "Remove task 2" → Task identified by ID, deleted
  - Test: "Delete all completed tasks" → Multiple deletions with summary (if supported)
  - Reference: spec.md lines 87-89

**Acceptance**: Agent can delete tasks by title or ID, confirms deletion

---

## Phase 8: Edge Cases, Error Handling, and Polish

**Goal**: Handle edge cases, improve error messages, validate stateless architecture

**Blocking**: Phase 7 must complete first (all user stories implemented)

- [x] [T034] [P2] [Polish] Implement UNKNOWN intent handling in agent.py
  - When intent confidence < 0.7 or no pattern matches, return UNKNOWN
  - Response: "I can only help with task management. Try 'create a task' or 'show my tasks'."
  - Test: "What is the weather today?" → Helpful guidance message
  - Reference: spec.md lines 95-96, quickstart.md lines 289-318

- [x] [T035] [P2] [Polish] Implement error translation in response_formatter.py
  - Add format_error_response(error_code: str, error_message: str) -> str function
  - Map error codes to user-friendly messages:
    - TASK_NOT_FOUND → "I couldn't find that task. Try listing your tasks first."
    - VALIDATION_ERROR → "Invalid input: {details}"
    - DATABASE_ERROR → "Something went wrong. Please try again."
  - Reference: spec.md lines 97-99, data-model.md lines 264-281

- [ ] [T036] [P3] [Polish] Implement ambiguous task reference handling in agent.py
  - When identify_task finds multiple matches (>1 task with >70% similarity), return list
  - Response: "I found multiple tasks matching '{query}'. Which one? (1) {title1} (2) {title2}"
  - Or use most recent match with confidence indicator
  - Test: "Complete the milk task" when multiple tasks contain "milk"
  - Reference: spec.md lines 96-97, quickstart.md lines 443-488

- [x] [T037] [P2] [Polish] Add input validation in agent_routes.py
  - Validate user_id is non-empty string
  - Validate message is 1-1000 characters
  - Return HTTP 400 with clear error message for validation failures
  - Reference: contracts/agent_endpoint.json lines 141-170

- [x] [T038] [P2] [Polish] Add execution time tracking in agent.py
  - Track start_time at beginning of process_request
  - Calculate execution_time_ms at end
  - Include in AgentResponse metadata
  - Reference: contracts/agent_endpoint.json lines 247-253

- [x] [T039] [P1] [Polish] Verify stateless architecture
  - Ensure no module-level variables (except constants)
  - Ensure no class instances with mutable state
  - All functions are pure (same input → same output)
  - Test: Process 1000 requests, verify no memory accumulation
  - Reference: research.md lines 133-159, spec.md line 114

- [ ] [T040] [P2] [Polish] Add LLM fallback for intent classification in intent_parser.py
  - When rule-based classification confidence < 0.7, use LLM
  - Create classify_with_llm(message: str) -> IntentClassification function
  - Use Gemini model to classify intent and extract parameters
  - Reference: research.md Decision 2 (lines 29-57)

- [ ] [T041] [P3] [Polish] Implement parameter extraction for complex cases in intent_parser.py
  - Extract priority from keywords: "high", "medium", "low"
  - Extract due_date from temporal expressions: "tomorrow", "Friday", "next week"
  - Use simple regex patterns or date parsing library
  - Reference: research.md lines 201-207

- [x] [T042] [P2] [Polish] Add comprehensive error handling in agent.py
  - Wrap all tool invocations in try-except blocks
  - Catch and translate all exceptions to user-friendly messages
  - Log errors for debugging (without exposing to user)
  - Never expose technical error details to user
  - Reference: research.md lines 208-216

- [x] [T043] [P3] [Polish] Create unit tests in backend/tests/agent/test_intent_parser.py
  - Test all intent patterns (CREATE, LIST, COMPLETE, UPDATE, DELETE)
  - Test parameter extraction (title, description, priority, due_date)
  - Test edge cases (empty message, very long message, ambiguous message)
  - Target: 95% code coverage for intent_parser.py
  - Reference: research.md lines 273-285

- [x] [T044] [P3] [Polish] Create unit tests in backend/tests/agent/test_response_formatter.py
  - Test all response templates (success and error cases)
  - Test response length constraints (<200 chars simple, <500 complex)
  - Test error message formatting
  - Target: 90% code coverage for response_formatter.py
  - Reference: research.md lines 273-285

- [x] [T045] [P2] [Polish] Create integration tests in backend/tests/agent/test_agent.py
  - Test end-to-end flow: user message → intent → tool call → response
  - Mock MCP tool responses (success and error cases)
  - Test all 5 user stories with acceptance scenarios
  - Test stateless verification (multiple requests, no state accumulation)
  - Target: 85% code coverage for agent.py
  - Reference: research.md lines 286-301, quickstart.md

- [x] [T046] [P2] [Polish] Performance testing and optimization
  - Test response time: 95% of requests < 2 seconds
  - Test concurrency: 100+ concurrent requests without errors
  - Test rule-based fast path: 95% of intents classified without LLM
  - Optimize if performance targets not met
  - Reference: plan.md lines 26-29, research.md lines 218-235

- [x] [T047] [P1] [Polish] Security testing - user isolation
  - Create tasks for user-A and user-B
  - Verify user-A cannot access user-B's tasks
  - Verify all tool calls include correct user_id
  - Verify TASK_NOT_FOUND returned (not permission denied)
  - Reference: research.md lines 246-259, quickstart.md lines 356-391

- [x] [T048] [P2] [Polish] Update API documentation
  - Document POST /api/agent/chat endpoint in API docs
  - Include request/response examples from contracts/agent_endpoint.json
  - Document error codes and responses
  - Add usage examples for all 5 user stories

- [ ] [T049] [P3] [Polish] Create manual testing guide
  - Document how to start agent endpoint
  - Provide curl commands for all test scenarios from quickstart.md
  - Include troubleshooting section
  - Reference: quickstart.md lines 23-631

**Acceptance**: All edge cases handled, errors translated to user-friendly messages, stateless architecture verified, tests passing, performance targets met

---

## Summary

**Total Tasks**: 49 tasks across 8 phases
**Critical Path**: Phase 1 → Phase 2 → Phase 3 (MVP) → Phase 4-7 (remaining user stories) → Phase 8 (polish)
**MVP Milestone**: Phase 3 complete (T001-T016) - Agent can create tasks via natural language
**Estimated Effort**:
- Phase 1-2 (Setup + Foundation): 6-8 hours
- Phase 3 (US1 - MVP): 8-10 hours
- Phase 4-7 (US2-US5): 12-16 hours
- Phase 8 (Polish): 10-12 hours
- **Total**: 36-46 hours

**Key Dependencies**:
- MCP tools (004-mcp-task-tools) must be implemented and accessible
- Gemini API key must be available
- OpenAI Agent SDK must be compatible with Gemini routing

**Risk Mitigation**:
- Start with MVP (Phase 3) to validate core concept early
- Test stateless architecture continuously (no state accumulation)
- Validate user isolation in every phase
- Monitor performance against <2s target throughout development

**Success Criteria** (from spec.md):
- ✅ 95%+ intent classification accuracy
- ✅ 98%+ correct tool invocation rate
- ✅ <2 second response time (95th percentile)
- ✅ Zero state accumulation (verified over 1000 requests)
- ✅ 100% graceful error handling
- ✅ Concise responses (<200 chars simple, <500 complex)
- ✅ 90%+ parameter extraction accuracy
- ✅ 100% ambiguity handling (no crashes)
- ✅ User isolation enforced (cross-user access blocked)
- ✅ 100% helpful guidance for non-task messages
