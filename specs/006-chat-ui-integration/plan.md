# Implementation Plan: Chat UI & End-to-End Integration

**Branch**: `006-chat-ui-integration` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-chat-ui-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a conversational chat interface that integrates Frontend (Next.js) → Agent (stateless) → Backend APIs for natural language task management. Users can create, view, update, complete, and delete todos via chat without leaving the conversational interface. The implementation embeds a chat UI into the existing frontend layout, connects to the stateless agent endpoint (POST /api/v1/agent/chat), and ensures seamless end-to-end flow with real backend data. Chat messages are maintained in-memory only (no persistence), and the UI matches the existing application theme for visual consistency.

**Key Approach**:
1. Embed chat UI component into existing Next.js App Router layout
2. Define minimal chat message schema (user_message, agent_response, status)
3. Connect chat input to agent endpoint with JWT token forwarding
4. Map agent intents to MCP tools (create/read/update/delete todos)
5. Ensure backend responses sync UI state correctly
6. Implement graceful error handling (auth, validation, network)
7. Validate end-to-end flow with real backend data
8. Remove unused UI components, mocks, or temp files

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend - existing)
**Primary Dependencies**:
- Frontend: Next.js 16.0.1 (App Router), React 18+, Tailwind CSS, TypeScript
- Backend: FastAPI (existing), SQLModel (existing), OpenAI Agent SDK 0.8.1 (existing)

**Storage**:
- Database: Neon Serverless PostgreSQL (existing - for task data)
- Chat State: In-memory only (no persistence per spec requirements)
- Authentication: JWT tokens in localStorage/cookies

**Testing**:
- Frontend: Jest + React Testing Library (unit tests), Playwright (E2E tests)
- Backend: pytest (existing - agent endpoint already tested)

**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge latest versions), responsive design (mobile 320px+, tablet 768px+, desktop 1024px+)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Agent response latency: <2 seconds (p95)
- Chat page load time: <1 second
- Message rendering: <50ms
- Auto-scroll performance: 60fps smooth scrolling

**Constraints**:
- MUST use stateless agent architecture (no state between requests)
- MUST NOT persist chat history to database (in-memory only)
- MUST match existing application theme (colors, fonts, spacing)
- MUST pass JWT token with every agent request
- MUST handle DELETE operation limitation (80% success rate acceptable)
- MUST reuse existing UI components where possible
- MUST NOT implement streaming responses (single response per request)

**Scale/Scope**:
- Single chat page route (/chat)
- 5 task operations (create, list, complete, update, delete)
- Minimal UI components (ChatContainer, MessageList, MessageInput, Message)
- No chat history persistence (session-only)
- Support for 100+ messages in single session without performance degradation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development
- ✅ PASS: Feature spec exists at `specs/006-chat-ui-integration/spec.md`
- ✅ PASS: Spec includes 8 prioritized user stories with acceptance criteria
- ✅ PASS: Spec includes 20 functional requirements
- ✅ PASS: Implementation plan being created before tasks
- ✅ PASS: Tasks will be generated from this plan via `/sp.tasks`

### Principle II: Zero Manual Coding
- ✅ PASS: All code will be generated via Claude Code
- ✅ PASS: Frontend Agent will be used for Next.js components
- ✅ PASS: Backend Agent will be used if agent endpoint needs modifications
- ✅ PASS: No manual coding planned

### Principle III: Security-First Architecture
- ✅ PASS: All chat requests will require valid JWT authentication
- ✅ PASS: JWT token will be passed in Authorization header
- ✅ PASS: Agent endpoint already enforces user_id isolation (Feature 005)
- ✅ PASS: No hardcoded secrets (agent endpoint URL from environment)
- ✅ PASS: Input sanitization to prevent XSS attacks
- ✅ PASS: Output sanitization before rendering agent responses

### Principle IV: Technology Stack Adherence
- ✅ PASS: Frontend uses Next.js 16+ with App Router (existing)
- ✅ PASS: Frontend uses Tailwind CSS for styling (existing)
- ✅ PASS: Frontend uses TypeScript (existing)
- ✅ PASS: Backend uses FastAPI (existing)
- ✅ PASS: Backend uses stateless agent with OpenAI SDK (existing - Feature 005)
- ✅ PASS: Database is Neon PostgreSQL (existing)
- ✅ PASS: Authentication uses JWT tokens (existing - Feature 002)

### Principle V: API Contract Discipline
- ✅ PASS: Frontend will communicate with backend via REST API
- ✅ PASS: Agent endpoint already defined: POST /api/v1/agent/chat
- ✅ PASS: Request/response schemas already defined (AgentRequest, AgentResponse)
- ✅ PASS: No business logic in frontend (only presentation and API calls)
- ✅ PASS: Error responses include detail and code fields

### Principle VI: Secrets Management
- ✅ PASS: No secrets in frontend code
- ✅ PASS: JWT token stored securely (localStorage or httpOnly cookies)
- ✅ PASS: Agent endpoint URL from environment variable
- ✅ PASS: No hardcoded credentials

### Principle VII: Stateless Architecture (Phase III)
- ✅ PASS: Agent is stateless (Feature 005 already implemented)
- ✅ PASS: Chat messages stored in-memory only (no database persistence per spec)
- ✅ PASS: No in-memory state on backend (agent is stateless)
- ✅ PASS: Each request is independent

**Note on Chat Persistence**: This feature intentionally does NOT persist chat history to database per spec requirements (FR-018, FR-019, OOS-001). Chat messages are maintained in-memory on the frontend only for the current session. This differs from typical Phase III requirements but is explicitly specified for this feature.

### Principle VIII: MCP Tool Standards (Phase III)
- ✅ PASS: MCP tools already implemented in Feature 005
- ✅ PASS: All tools have Pydantic input/output schemas
- ✅ PASS: All tools enforce user_id ownership
- ✅ PASS: All tools are stateless and database-backed
- ✅ PASS: Chat UI will invoke agent, which uses MCP tools

### Principle IX: Agent-Tool Interaction Rules (Phase III)
- ✅ PASS: Agent uses MCP tools for all task operations (Feature 005)
- ✅ PASS: Agent does not access database directly
- ✅ PASS: Agent validates tool responses
- ✅ PASS: Agent handles tool errors gracefully
- ✅ PASS: DELETE operation has known limitation (80% success rate documented)

**Constitution Check Result**: ✅ ALL GATES PASSED - No violations, proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/006-chat-ui-integration/
├── spec.md              # Feature specification (COMPLETED)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (PENDING)
├── data-model.md        # Phase 1 output (PENDING)
├── quickstart.md        # Phase 1 output (PENDING)
├── contracts/           # Phase 1 output (PENDING)
│   ├── chat-api.json    # Agent endpoint contract (reference existing)
│   └── chat-ui.json     # Frontend component contracts
├── checklists/          # Requirements checklists (COMPLETED)
│   ├── ux.md            # 70 UX checklist items
│   ├── security.md      # 46 security checklist items
│   ├── performance.md   # 41 performance checklist items
│   └── test.md          # 102 testing checklist items
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)

backend/                          # Existing backend (NO CHANGES EXPECTED)
├── agent/                        # Feature 005 - Stateless agent (EXISTING)
│   ├── agent.py                  # Agent endpoint handler
│   ├── intent_parser.py          # Intent classification
│   └── response_formatter.py     # Response formatting
├── mcp/                          # Feature 004 - MCP tools (EXISTING)
│   ├── tools/                    # 5 MCP tools (list, add, complete, update, delete)
│   └── schemas/                  # Tool input/output schemas
├── api/                          # Feature 001 - Task APIs (EXISTING)
│   └── v1/
│       ├── auth.py               # Feature 002 - JWT auth (EXISTING)
│       ├── tasks.py              # Task CRUD endpoints (EXISTING)
│       └── agent.py              # Agent chat endpoint (EXISTING)
└── tests/                        # Backend tests (EXISTING)

frontend/                         # Existing frontend (MODIFICATIONS NEEDED)
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/               # Feature 003 - Auth pages (EXISTING)
│   │   ├── dashboard/            # Feature 003 - Dashboard (EXISTING)
│   │   ├── chat/                 # NEW - Chat page route
│   │   │   ├── page.tsx          # Chat page component
│   │   │   └── layout.tsx        # Chat layout (optional)
│   │   └── layout.tsx            # Root layout (EXISTING)
│   ├── components/               # React components
│   │   ├── ui/                   # Feature 003 - Existing UI components
│   │   └── chat/                 # NEW - Chat components
│   │       ├── ChatContainer.tsx # Main chat container
│   │       ├── MessageList.tsx   # Message list with auto-scroll
│   │       ├── MessageInput.tsx  # Input field with send button
│   │       ├── Message.tsx       # Single message component
│   │       └── LoadingIndicator.tsx # Loading state
│   ├── lib/                      # Utilities
│   │   ├── api.ts                # Feature 003 - API client (EXISTING)
│   │   └── chat-api.ts           # NEW - Chat API client
│   ├── hooks/                    # React hooks
│   │   └── useChat.ts            # NEW - Chat state management hook
│   └── types/                    # TypeScript types
│       └── chat.ts               # NEW - Chat message types
└── tests/                        # Frontend tests
    └── chat/                     # NEW - Chat component tests
        ├── ChatContainer.test.tsx
        ├── MessageList.test.tsx
        ├── MessageInput.test.tsx
        └── useChat.test.ts
```

**Structure Decision**: Web application structure with existing frontend and backend. This feature adds a new `/chat` route to the frontend with minimal new components. The backend agent endpoint (POST /api/v1/agent/chat) already exists from Feature 005, so no backend changes are expected unless bugs are discovered during integration testing.

**Key Integration Points**:
1. Frontend `/chat` page → Backend `/api/v1/agent/chat` endpoint
2. JWT token from existing auth system (Feature 002)
3. Agent endpoint → MCP tools (Feature 004) → Backend APIs (Feature 001)
4. Chat UI components reuse existing theme from Feature 003

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied:
- Spec-driven development followed
- Zero manual coding (Claude Code agents)
- Security-first (JWT auth enforced)
- Technology stack adhered to (Next.js, FastAPI, Neon PostgreSQL)
- API contract discipline maintained
- Stateless architecture (agent is stateless, chat is in-memory)
- MCP tools already implemented and compliant
- Agent-tool interaction rules followed

**No complexity justification required.**

## Phase 0: Research & Unknowns

### Research Questions

The following questions need to be researched before detailed design:

1. **Chat UI Component Library**
   - Question: Should we use an existing chat UI library (e.g., react-chat-elements, @chatscope/chat-ui-kit-react) or build custom components?
   - Why: Existing libraries may speed up development but could conflict with theme requirements
   - Research needed: Evaluate libraries for theme customization, bundle size, and Tailwind CSS compatibility

2. **Chat State Management**
   - Question: Should we use React Context, Zustand, or simple useState for chat state?
   - Why: Need to manage messages, loading state, and errors efficiently
   - Research needed: Compare approaches for simplicity, performance, and testability

3. **Message Rendering Optimization**
   - Question: How to optimize rendering for 100+ messages without performance degradation?
   - Why: Spec requires support for 100+ messages with smooth scrolling
   - Research needed: Investigate virtualization (react-window, react-virtuoso) vs simple optimization

4. **Auto-Scroll Implementation**
   - Question: What's the best approach for auto-scrolling to latest message?
   - Why: Must scroll smoothly (60fps) and handle edge cases (user scrolled up, new message arrives)
   - Research needed: Best practices for scroll behavior and user experience

5. **Error Handling Patterns**
   - Question: How to handle network errors, timeout errors, and agent errors consistently?
   - Why: Spec requires graceful error handling with user-friendly messages
   - Research needed: Error boundary patterns, retry logic, and error message design

6. **JWT Token Management**
   - Question: Where is JWT token currently stored (localStorage, cookies, httpOnly cookies)?
   - Why: Need to retrieve token for Authorization header
   - Research needed: Review Feature 002 implementation for token storage location

7. **Theme Integration**
   - Question: What are the exact theme variables (colors, fonts, spacing) used in existing UI?
   - Why: Chat UI must match existing theme exactly (100% consistency per SC-003)
   - Research needed: Extract theme variables from existing components

8. **Input Sanitization**
   - Question: What sanitization library should we use to prevent XSS attacks?
   - Why: Security requirement to sanitize user input and agent responses
   - Research needed: Evaluate DOMPurify, sanitize-html, or built-in browser APIs

### Research Outputs

Research findings will be documented in `research.md` with the following structure:

```markdown
# Research: Chat UI & End-to-End Integration

## Decision 1: Chat UI Component Library
- **Decision**: [Build custom components | Use library X]
- **Rationale**: [Why this approach was chosen]
- **Alternatives Considered**: [Other options evaluated]
- **Implementation Notes**: [Key details for tasks]

## Decision 2: Chat State Management
- **Decision**: [useState | Context | Zustand]
- **Rationale**: [Why this approach was chosen]
- **Alternatives Considered**: [Other options evaluated]
- **Implementation Notes**: [Key details for tasks]

[... continue for all research questions]
```

## Phase 1: Design & Contracts

### Data Model

The following entities will be documented in `data-model.md`:

1. **ChatMessage** (Frontend only - in-memory)
   - Fields: id, text, sender, timestamp, status
   - Validation: text max 1000 chars, sender enum (user|agent)
   - State transitions: sending → sent → error

2. **ChatSession** (Frontend only - in-memory)
   - Fields: messages[], isLoading, error
   - Lifecycle: created on page load, destroyed on navigation

3. **AgentRequest** (API contract - existing)
   - Fields: user_id, message
   - Validation: user_id required, message 1-1000 chars

4. **AgentResponse** (API contract - existing)
   - Fields: response, metadata
   - Validation: response required, metadata optional

### API Contracts

The following contracts will be documented in `contracts/`:

1. **chat-api.json** (Reference existing agent endpoint)
   - Endpoint: POST /api/v1/agent/chat
   - Request: AgentRequest schema
   - Response: AgentResponse schema
   - Errors: 401 (unauthorized), 400 (validation), 500 (server error)

2. **chat-ui.json** (Frontend component contracts)
   - ChatContainer props and events
   - MessageList props and events
   - MessageInput props and events
   - Message props and rendering

### Integration Scenarios

The following scenarios will be documented in `quickstart.md`:

1. **Happy Path**: User sends message → Agent responds → Message displayed
2. **Create Task**: User types "Create a task to buy milk" → Agent creates task → Confirmation displayed
3. **List Tasks**: User types "Show my tasks" → Agent lists tasks → Tasks displayed
4. **Complete Task**: User types "Complete task 1" → Agent marks complete → Confirmation displayed
5. **Error Handling**: Network error → User-friendly error message → Retry option
6. **Authentication**: Token expired → Redirect to login → Return to chat after login

## Phase 2: Task Breakdown

Task breakdown will be generated via `/sp.tasks` command after Phase 1 is complete.

**Expected Task Categories**:
1. **Setup Tasks**: Create chat route, install dependencies
2. **Component Tasks**: Build ChatContainer, MessageList, MessageInput, Message components
3. **Integration Tasks**: Connect to agent endpoint, implement JWT token passing
4. **State Management Tasks**: Implement useChat hook, handle loading/error states
5. **Styling Tasks**: Match existing theme, ensure responsive design
6. **Error Handling Tasks**: Implement network error handling, timeout handling
7. **Testing Tasks**: Unit tests, integration tests, E2E tests
8. **Polish Tasks**: Auto-scroll optimization, loading indicators, accessibility

## Dependencies

### Internal Dependencies (CRITICAL)

- **Feature 005-stateless-task-agent**: Agent endpoint must be fully functional
  - Status: ✅ COMPLETED (91/91 tests passing, 4/5 operations working)
  - Endpoint: POST /api/v1/agent/chat
  - Known limitation: DELETE operation has 80% success rate (acceptable per user decision)

- **Feature 003-frontend-todo-ui**: Frontend codebase and theme must exist
  - Status: ✅ COMPLETED
  - Provides: Next.js App Router, Tailwind CSS theme, existing UI components

- **Feature 002-backend-jwt-auth**: JWT authentication must be working
  - Status: ✅ COMPLETED
  - Provides: JWT token generation, token verification, user_id extraction

- **Feature 001-backend-task-api**: Backend task APIs must be operational
  - Status: ✅ COMPLETED
  - Provides: Task CRUD operations, database schema

### External Dependencies

- Next.js 16.0.1 (existing)
- React 18+ (existing)
- Tailwind CSS (existing)
- TypeScript 5.x (existing)
- JWT token management (existing)

### Dependency Verification

Before starting implementation, verify:
1. ✅ Agent endpoint responds to POST /api/v1/agent/chat
2. ✅ JWT token can be retrieved from storage
3. ✅ Existing theme variables are documented
4. ✅ All 4 internal dependencies are completed

## Risks & Mitigations

### Risk 1: DELETE Operation Limitation
- **Risk**: DELETE operation has 80% success rate due to parameter extraction issues
- **Impact**: Medium - Users may experience failures when deleting tasks via chat
- **Mitigation**: Document limitation in UI, provide guidance for successful deletion patterns
- **Status**: Accepted by user, documented in spec

### Risk 2: Theme Consistency
- **Risk**: Chat UI may not perfectly match existing theme
- **Impact**: Medium - Affects user experience and perceived quality
- **Mitigation**: Extract theme variables early, conduct visual QA, reuse existing components
- **Status**: Mitigated by research phase

### Risk 3: Performance with Many Messages
- **Risk**: Chat may become slow with 100+ messages
- **Impact**: Medium - Affects user experience
- **Mitigation**: Research virtualization, implement performance optimizations, test with large message counts
- **Status**: Mitigated by research and testing

### Risk 4: Agent Response Latency
- **Risk**: Agent responses may exceed 2 second target
- **Impact**: High - Poor user experience
- **Mitigation**: Implement loading indicators, set timeout at 30 seconds, monitor p95 latency
- **Status**: Mitigated by existing agent performance (p95 < 2s verified in Feature 005)

### Risk 5: Authentication Token Expiry
- **Risk**: JWT token may expire during chat session
- **Impact**: Medium - Users lose ability to send messages
- **Mitigation**: Implement token refresh logic, display clear error message, provide login button
- **Status**: Mitigated by error handling design

## Success Criteria

Implementation is considered successful when:

1. ✅ All 8 user stories from spec are implemented and tested
2. ✅ All 259 checklist items pass (70 UX + 46 security + 41 performance + 102 testing)
3. ✅ Chat UI matches existing theme with 100% consistency
4. ✅ Agent responses appear within 2 seconds (p95)
5. ✅ All 5 task operations work via chat (4/5 at 95%+, DELETE at 80%)
6. ✅ Error handling is graceful and user-friendly
7. ✅ Chat interface is responsive on mobile, tablet, and desktop
8. ✅ No unused components or mock files remain in codebase
9. ✅ All tests pass (unit, integration, E2E)
10. ✅ Constitution compliance verified (all gates pass)

## Next Steps

1. **Phase 0**: Generate `research.md` by researching all unknowns listed above
2. **Phase 1**: Generate `data-model.md`, `contracts/`, and `quickstart.md` based on research findings
3. **Phase 1**: Update agent context with new technologies (if any)
4. **Phase 2**: Generate `tasks.md` via `/sp.tasks` command
5. **Implementation**: Execute tasks via `/sp.implement` command using Frontend Agent

**Command to proceed**: `/sp.tasks` (after Phase 0 and Phase 1 are complete)
