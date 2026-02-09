---
description: "Task list for Chat UI & End-to-End Integration using OpenAI ChatKit"
---

# Tasks: Chat UI & End-to-End Integration

**Input**: Design documents from `/specs/006-chat-ui-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Approach**: Using **OpenAI ChatKit** (`@openai/chatkit-react`) instead of custom components. ChatKit handles message rendering, state management, auto-scroll, loading states, and error display automatically.

**Tests**: Tests are NOT included as they were not requested in the feature specification.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow the project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install ChatKit and verify prerequisites

- [ ] T001 Install ChatKit package: Run `npm install @openai/chatkit-react` in frontend directory
- [ ] T002 Verify Next.js 16.0.1 and React 18+ dependencies are installed in frontend/package.json
- [ ] T003 [P] Verify existing JWT token management implementation in frontend/src/lib/api.ts or frontend/src/lib/auth.ts
- [ ] T004 [P] Create chat directory structure: `frontend/src/app/chat/`, `frontend/src/components/chat/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core ChatKit integration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Verify agent endpoint is accessible at http://localhost:8000/api/v1/agent/chat by making a test request with JWT token
- [ ] T006 Create custom fetch function in frontend/src/lib/chatkit-fetch.ts that injects JWT token into ChatKit requests (Authorization: Bearer header)
- [ ] T007 Create ChatKitWrapper component in frontend/src/components/chat/ChatKitWrapper.tsx that initializes useChatKit with custom fetch and agent endpoint
- [ ] T008 Configure ChatKit in ChatKitWrapper: set api.url to agent endpoint, disable streaming (single response mode), enable history (in-memory only)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Chat Interaction (Priority: P1) 🎯 MVP

**Goal**: Provide a working chat interface where users can send messages and receive responses from the AI agent

**Independent Test**: Log in, navigate to /chat, type "Hello" or "Show my tasks", and verify agent responds with a message

### Implementation for User Story 1

- [ ] T009 Configure ChatKit startScreen in ChatKitWrapper with greeting: "How can I help you with your tasks today?" and prompts: ["Show my tasks", "Create a task"]
- [ ] T010 Configure ChatKit composer in ChatKitWrapper with placeholder: "Ask me anything about your tasks..."
- [ ] T011 Configure ChatKit header and history settings: header disabled, history enabled (in-memory)
- [ ] T012 Create chat page route in frontend/src/app/chat/page.tsx that renders ChatKitWrapper with authentication check
- [ ] T013 Use Next.js dynamic import in chat page to load ChatKitWrapper (SSR-safe: `dynamic(() => import('@/components/chat/ChatKitWrapper'), { ssr: false })`)
- [ ] T014 Add navigation link to chat page in existing layout/navigation component (frontend/src/app/layout.tsx or frontend/src/components/Navigation.tsx)
- [ ] T015 Test basic chat flow: send "Hello" message and verify agent responds with a message
- [ ] T016 Test ChatKit auto-scroll: send multiple messages and verify chat scrolls to latest message automatically
- [ ] T017 Test ChatKit loading indicator: verify "Agent is thinking..." appears while waiting for response

**Checkpoint**: At this point, User Story 1 should be fully functional - users can send messages and receive responses

---

## Phase 4: User Story 2 - Create Tasks via Chat (Priority: P2)

**Goal**: Enable users to create new tasks by typing natural language commands like "Create a task to buy groceries"

**Independent Test**: Type "Create a task to buy milk" and verify: (1) agent confirms task creation, (2) task appears in backend database, (3) subsequent "Show my tasks" includes the new task

### Implementation for User Story 2

- [ ] T018 [US2] Verify agent endpoint correctly handles "create task" intent by testing with sample messages like "Create a task to buy milk"
- [ ] T019 [US2] Test task creation with various formats: "Create a task to X", "Add a task X", "Remind me to X"
- [ ] T020 [US2] Test task creation with priority: "Add a high priority task to finish report"
- [ ] T021 [US2] Test task creation with description: "Remind me to call dentist with description: annual checkup"
- [ ] T022 [US2] Verify ChatKit displays agent's confirmation message correctly (e.g., "Task created: Buy milk")

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can create tasks via chat

---

## Phase 5: User Story 3 - View Tasks via Chat (Priority: P2)

**Goal**: Enable users to view their tasks by typing commands like "Show my tasks" or "What are my high priority tasks"

**Independent Test**: Create a few tasks via API or UI, then type "Show my tasks" in chat and verify agent lists all tasks with correct details

### Implementation for User Story 3

- [ ] T023 [US3] Verify agent endpoint correctly handles "list tasks" intent by testing with "Show my tasks"
- [ ] T024 [US3] Test viewing all tasks: "Show my tasks"
- [ ] T025 [US3] Test filtering by priority: "Show my high priority tasks"
- [ ] T026 [US3] Test filtering by completion: "Show my completed tasks"
- [ ] T027 [US3] Test empty state: "Show my tasks" when user has no tasks
- [ ] T028 [US3] Verify ChatKit displays task lists correctly with proper formatting

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - users can create and view tasks via chat

---

## Phase 6: User Story 4 - Complete Tasks via Chat (Priority: P2)

**Goal**: Enable users to mark tasks as complete by typing commands like "Complete task 5" or "Mark 'buy groceries' as done"

**Independent Test**: Create a task, then type "Complete task 1" and verify: (1) agent confirms completion, (2) task status updates in database, (3) subsequent "Show my tasks" shows task as completed

### Implementation for User Story 4

- [ ] T029 [US4] Verify agent endpoint correctly handles "complete task" intent by testing with "Complete task 1"
- [ ] T030 [US4] Test completing task by ID: "Complete task 5"
- [ ] T031 [US4] Test completing task by title: "Mark 'buy groceries' as done"
- [ ] T032 [US4] Test uncompleting task: "Undo completion of task 3"
- [ ] T033 [US4] Test error handling for non-existent task: "Complete task 999"
- [ ] T034 [US4] Verify ChatKit displays agent's confirmation message correctly

**Checkpoint**: At this point, User Stories 1-4 should all work - users can create, view, and complete tasks via chat

---

## Phase 7: User Story 5 - Update Tasks via Chat (Priority: P3)

**Goal**: Enable users to update task details by typing commands like "Change task 3 to 'Buy organic milk'" or "Update task description"

**Independent Test**: Create a task, then type "Change task 1 to 'New title'" and verify: (1) agent confirms update, (2) task title updates in database, (3) subsequent "Show my tasks" shows updated title

### Implementation for User Story 5

- [ ] T035 [US5] Verify agent endpoint correctly handles "update task" intent by testing with "Change task 1 to 'New title'"
- [ ] T036 [US5] Test updating task title by ID: "Change task 3 to 'Buy organic milk'"
- [ ] T037 [US5] Test updating task description: "Update 'Call dentist' description to 'Annual checkup appointment'"
- [ ] T038 [US5] Test error handling for non-existent task: "Update task 999"
- [ ] T039 [US5] Verify ChatKit displays agent's confirmation message correctly

**Checkpoint**: At this point, User Stories 1-5 should all work - users can create, view, complete, and update tasks via chat

---

## Phase 8: User Story 6 - Delete Tasks via Chat (Priority: P3)

**Goal**: Enable users to delete tasks by typing commands like "Delete task 5" or "Remove 'buy groceries'"

**Independent Test**: Create a task, then type "Delete task 1" and verify: (1) agent confirms deletion, (2) task is removed from database, (3) subsequent "Show my tasks" doesn't include deleted task

**Note**: DELETE operation has known 80% success rate due to parameter extraction issues in the agent (documented in spec)

### Implementation for User Story 6

- [ ] T040 [US6] Verify agent endpoint correctly handles "delete task" intent by testing with "Delete task 1"
- [ ] T041 [US6] Test deleting task by ID: "Delete task 5"
- [ ] T042 [US6] Test deleting task by title: "Remove 'buy groceries'"
- [ ] T043 [US6] Test error handling for non-existent task: "Delete task 999"
- [ ] T044 [US6] Document DELETE operation limitation in chat UI (e.g., help text or error message guidance)
- [ ] T045 [US6] Verify ChatKit displays agent's confirmation or error message correctly

**Checkpoint**: At this point, User Stories 1-6 should all work - users can perform all CRUD operations via chat

---

## Phase 9: User Story 7 - Error Handling and User Feedback (Priority: P3)

**Goal**: Provide clear, helpful error messages when something goes wrong (network error, invalid command, server error)

**Independent Test**: Simulate various error conditions (disconnect backend, send invalid commands, trigger database errors) and verify agent provides user-friendly error messages

### Implementation for User Story 7

- [ ] T046 [US7] Implement network error handling in custom fetch function (chatkit-fetch.ts) with try-catch and user-friendly error messages
- [ ] T047 [US7] Implement timeout handling in custom fetch function (30 second timeout with AbortController)
- [ ] T048 [US7] Implement authentication error handling in custom fetch: detect 401 responses and redirect to login
- [ ] T049 [US7] Implement server error handling in custom fetch: detect 500 responses and show user-friendly message
- [ ] T050 [US7] Test network error: disconnect backend and send message, verify ChatKit displays error message
- [ ] T051 [US7] Test invalid command: send "Make me coffee" and verify agent responds with helpful guidance
- [ ] T052 [US7] Test authentication expiry: simulate expired token and verify redirect to login
- [ ] T053 [US7] Test server error: simulate 500 error and verify ChatKit displays graceful error message
- [ ] T054 [US7] Install DOMPurify: Run `npm install dompurify @types/dompurify` for extra XSS protection
- [ ] T055 [US7] Sanitize agent responses in custom fetch before returning to ChatKit (use DOMPurify to strip HTML tags)

**Checkpoint**: At this point, all error scenarios should be handled gracefully with user-friendly messages

---

## Phase 10: User Story 8 - UI Theme Consistency and Polish (Priority: P4)

**Goal**: Ensure chat interface matches the existing application theme and design language for a cohesive, professional experience

**Independent Test**: Compare chat UI colors, fonts, spacing, and component styles against existing application pages and verify they match

### Implementation for User Story 8

- [ ] T056 [P] [US8] Extract existing theme variables from frontend/tailwind.config.js and document colors, fonts, spacing
- [ ] T057 [P] [US8] Review existing UI components in frontend/src/components/ui/ to identify reusable patterns
- [ ] T058 [US8] Create ChatKit custom styles in frontend/src/components/chat/ChatKitWrapper.module.css
- [ ] T059 [US8] Apply theme colors to ChatKit via CSS custom properties (--chatkit-primary, --chatkit-background, etc.)
- [ ] T060 [US8] Apply theme fonts and typography to ChatKit components via CSS
- [ ] T061 [US8] Apply theme spacing and padding to ChatKit container via CSS
- [ ] T062 [US8] Style ChatKit loading indicator to match existing loading states in the application
- [ ] T063 [US8] Style ChatKit composer (input area) to match existing input/button styles
- [ ] T064 [US8] Implement responsive design for mobile (320px width minimum) via CSS media queries
- [ ] T065 [US8] Implement responsive design for tablet (768px width) via CSS media queries
- [ ] T066 [US8] Test chat UI on mobile device and verify responsiveness
- [ ] T067 [US8] Test chat UI on tablet device and verify responsiveness
- [ ] T068 [US8] Test chat UI on desktop and verify theme consistency with other pages
- [ ] T069 [US8] Add accessibility attributes to ChatKitWrapper (ARIA labels for screen readers)
- [ ] T070 [US8] Test ChatKit performance with 100+ messages (verify no lag or memory issues)
- [ ] T071 [US8] Conduct visual QA: compare chat page side-by-side with dashboard page for theme consistency

**Checkpoint**: All user stories should now be complete with polished, theme-consistent UI

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [ ] T072 [P] Add "Clear chat" button to ChatKitWrapper to reset message history (optional enhancement)
- [ ] T073 [P] Add timestamps to messages via ChatKit configuration (optional enhancement per FR-015)
- [ ] T074 Code cleanup: remove any unused imports, console.logs, or commented code
- [ ] T075 Verify no mock data or temporary files remain in codebase
- [ ] T076 Update navigation to highlight active chat page when user is on /chat
- [ ] T077 Add loading state to chat page while verifying authentication
- [ ] T078 Test full end-to-end workflow: login → navigate to chat → create task → view tasks → complete task → delete task
- [ ] T079 Verify all 20 functional requirements from spec.md are implemented
- [ ] T080 Verify all 10 success criteria from spec.md are met
- [ ] T081 Document any known limitations or issues in specs/006-chat-ui-integration/README.md (if needed)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-10)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 11)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after US1 is complete - Depends on basic chat UI
- **User Story 3 (P2)**: Can start after US1 is complete - Depends on basic chat UI
- **User Story 4 (P2)**: Can start after US1 is complete - Depends on basic chat UI
- **User Story 5 (P3)**: Can start after US1 is complete - Depends on basic chat UI
- **User Story 6 (P3)**: Can start after US1 is complete - Depends on basic chat UI
- **User Story 7 (P3)**: Can start after US1 is complete - Enhances error handling across all stories
- **User Story 8 (P4)**: Can start after US1 is complete - Polishes UI across all stories

### Within Each User Story

- Core implementation before testing
- Verification tasks before moving to next story
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- Foundational tasks should run sequentially (they build on each other)
- Once US1 (Basic Chat Interaction) is complete, US2-US6 can potentially run in parallel as they all add functionality to the same chat interface
- US7 (Error Handling) and US8 (Theme Consistency) can run in parallel with each other after US1 is complete
- All Polish tasks marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (install ChatKit)
2. Complete Phase 2: Foundational (ChatKit integration)
3. Complete Phase 3: User Story 1 (Basic Chat Interaction)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add User Story 6 → Test independently → Deploy/Demo
8. Add User Story 7 → Test independently → Deploy/Demo
9. Add User Story 8 → Test independently → Deploy/Demo
10. Each story adds value without breaking previous stories

### Sequential Strategy (Recommended)

Given that all user stories build on the same chat interface:

1. Complete Setup + Foundational
2. Complete US1 (Basic Chat) - This is the foundation for all other stories
3. Complete US2-US6 sequentially (task operations) - Each adds a new operation
4. Complete US7 (Error Handling) - Enhances all previous stories
5. Complete US8 (Theme Consistency) - Final polish
6. Complete Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable after US1 is complete
- **ChatKit handles**: message rendering, state management, auto-scroll, loading states, error display
- **We handle**: JWT authentication, custom fetch, theme styling, connecting to agent endpoint
- Backend agent endpoint already exists - no backend changes needed
- DELETE operation has known 80% success rate (acceptable per spec)
- Chat history is in-memory only (no database persistence)
- No streaming responses (single response per request)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently

---

## Key ChatKit Configuration

```typescript
// frontend/src/components/chat/ChatKitWrapper.tsx
import { useChatKit } from '@openai/chatkit-react';
import { customFetch } from '@/lib/chatkit-fetch';

const { control } = useChatKit({
  api: {
    url: 'http://localhost:8000/api/v1/agent/chat',
    fetch: customFetch, // Inject JWT token
  },
  startScreen: {
    greeting: 'How can I help you with your tasks today?',
    prompts: [
      { label: 'Show my tasks', prompt: 'Show my tasks' },
      { label: 'Create a task', prompt: 'Create a task to...' },
    ],
  },
  composer: {
    placeholder: 'Ask me anything about your tasks...',
  },
  header: { enabled: false },
  history: { enabled: true }, // In-memory only
});
```

**Total Tasks**: 81 (reduced from 80 due to ChatKit simplification)
**Estimated Complexity**: Medium (ChatKit handles most complexity)
**MVP Path**: Phase 1 + Phase 2 + Phase 3 = 17 tasks = Working chat UI
