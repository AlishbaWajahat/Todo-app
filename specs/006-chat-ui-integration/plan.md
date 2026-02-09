# Implementation Plan: Chat UI & End-to-End Integration

**Branch**: `006-chat-ui-integration` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-chat-ui-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a conversational chat interface using **OpenAI ChatKit** that integrates Frontend (Next.js) → Agent (stateless) → Backend APIs for natural language task management. Users can create, view, update, complete, and delete todos via chat without leaving the conversational interface. The implementation integrates ChatKit into the existing Next.js App Router layout, connects to the stateless agent endpoint (POST /api/v1/agent/chat), and ensures seamless end-to-end flow with real backend data. Chat messages are maintained in-memory only (no persistence), and ChatKit is styled to match the existing application theme for visual consistency.

**Key Approach**:
1. Install and integrate OpenAI ChatKit (`@openai/chatkit-react`) into Next.js App Router
2. Configure ChatKit with custom fetch to connect to agent endpoint with JWT token forwarding
3. Configure ChatKit for NO streaming (single response per request) and NO database persistence (in-memory only)
4. Style ChatKit with CSS modules or Tailwind to match existing application theme
5. Map agent intents to MCP tools (create/read/update/delete todos) - backend already handles this
6. Ensure backend responses sync UI state correctly via ChatKit's built-in state management
7. Implement graceful error handling in custom fetch (auth, validation, network, timeout)
8. Validate end-to-end flow with real backend data
9. Test ChatKit integration on mobile, tablet, and desktop

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend - existing)
**Primary Dependencies**:
- Frontend: Next.js 16.0.1 (App Router), React 18+, Tailwind CSS, TypeScript
- **ChatKit**: `@openai/chatkit-react` (OpenAI's official chat UI library)
- **Sanitization**: DOMPurify for extra XSS protection
- Backend: FastAPI (existing), SQLModel (existing), OpenAI Agent SDK 0.8.1 (existing)

**Storage**:
- Database: Neon Serverless PostgreSQL (existing - for task data)
- Chat State: In-memory only via ChatKit (no persistence per spec requirements)
- Authentication: JWT tokens in localStorage/cookies

**Testing**:
- Frontend: Jest + React Testing Library (unit tests), Playwright (E2E tests)
- Backend: pytest (existing - agent endpoint already tested)

**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge latest versions), responsive design (mobile 320px+, tablet 768px+, desktop 1024px+)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Agent response latency: <2 seconds (p95)
- Chat page load time: <1 second
- ChatKit rendering: <50ms per message
- Auto-scroll performance: 60fps smooth scrolling (ChatKit built-in)

**Constraints**:
- MUST use stateless agent architecture (no state between requests)
- MUST NOT persist chat history to database (in-memory only via ChatKit)
- MUST use OpenAI ChatKit for UI (no custom components)
- MUST configure ChatKit for NO streaming (single response per request)
- MUST match existing application theme via ChatKit styling
- MUST pass JWT token with every agent request via custom fetch
- MUST handle DELETE operation limitation (80% success rate acceptable)
- MUST reuse existing UI components where possible (navigation, layout)
- MUST NOT implement streaming responses (single response per request)
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
│   │   │   └── page.tsx          # Chat page with ChatKit integration
│   │   └── layout.tsx            # Root layout (EXISTING)
│   ├── components/               # React components
│   │   ├── ui/                   # Feature 003 - Existing UI components
│   │   └── chat/                 # NEW - ChatKit wrapper components
│   │       ├── ChatKitWrapper.tsx # ChatKit integration component
│   │       └── ChatKitWrapper.module.css # Custom ChatKit styling (optional)
│   ├── lib/                      # Utilities
│   │   ├── api.ts                # Feature 003 - API client (EXISTING)
│   │   └── chatkit-config.ts     # NEW - ChatKit configuration and custom fetch
│   ├── hooks/                    # React hooks (if needed)
│   │   └── useChatKitAuth.ts     # NEW - JWT token management for ChatKit (optional)
│   └── types/                    # TypeScript types
│       └── chatkit.ts            # NEW - ChatKit type extensions (optional)
└── tests/                        # Frontend tests
    └── chat/                     # NEW - ChatKit integration tests
        └── ChatKitWrapper.test.tsx
```

**Structure Decision**: Web application structure with existing frontend and backend. This feature adds a new `/chat` route to the frontend using **OpenAI ChatKit** for the UI. ChatKit is a production-ready chat interface that handles message rendering, auto-scroll, loading states, and error display automatically. We only need to create a wrapper component to configure ChatKit and connect it to our existing agent endpoint. The backend agent endpoint (POST /api/v1/agent/chat) already exists from Feature 005, so no backend changes are expected unless bugs are discovered during integration testing.

**Key Integration Points**:
1. Frontend `/chat` page → ChatKit UI → Backend `/api/v1/agent/chat` endpoint
2. JWT token from existing auth system (Feature 002) passed via ChatKit custom fetch
3. Agent endpoint → MCP tools (Feature 004) → Backend APIs (Feature 001)
4. ChatKit styled with CSS to match existing theme from Feature 003
5. ChatKit configured for NO streaming and NO database persistence

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

### Research Status: ✅ COMPLETE

All technical unknowns have been resolved. Research findings documented in `research.md`.

### Key Decisions Made

1. **Chat UI Component Library**: ✅ Use OpenAI ChatKit (`@openai/chatkit-react`)
   - Production-ready, official OpenAI UI
   - Configurable for our constraints (no streaming, no persistence)
   - Handles message rendering, auto-scroll, loading states automatically

2. **Chat State Management**: ✅ Use ChatKit's built-in state management
   - ChatKit manages messages, loading, errors internally
   - We only manage JWT token and custom fetch

3. **Message Rendering Optimization**: ✅ Use ChatKit's built-in optimization
   - Production-tested for 100+ messages
   - No manual optimization needed

4. **Auto-Scroll Implementation**: ✅ Use ChatKit's built-in auto-scroll
   - Automatic, smooth 60fps animation
   - Handles edge cases (user scrolled up, etc.)

5. **Error Handling Patterns**: ✅ ChatKit errors + custom fetch error handling
   - ChatKit displays errors inline
   - Custom fetch handles auth, timeout, network errors

6. **JWT Token Management**: ✅ Retrieve from existing auth system (Feature 002)
   - Pass token via ChatKit custom fetch function
   - Handle token expiry (401 → redirect to login)

7. **Theme Integration**: ✅ Style ChatKit with CSS modules or Tailwind
   - Extract theme variables from tailwind.config.js
   - Apply custom styles to ChatKit components

8. **Input Sanitization**: ✅ ChatKit built-in + DOMPurify
   - ChatKit sanitizes by default
   - DOMPurify adds extra layer of security

**Research Output**: All decisions documented in `research.md` with rationale, alternatives considered, and implementation notes.

**ChatKit Configuration Summary**:
```typescript
// Install: npm install @openai/chatkit-react dompurify
import { useChatKit } from '@openai/chatkit-react';

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
  composer: { placeholder: 'Ask me anything about your tasks...' },
  header: { enabled: false },
  history: { enabled: true }, // In-memory only
  // NO streaming, NO database persistence
});
```

## Phase 1: Design & Contracts

### Data Model

The following entities are documented in `data-model.md`:

**Note**: ChatKit manages most chat state internally. We only need minimal custom types for integration.

1. **ChatKit Internal State** (managed by ChatKit)
   - Messages array (ChatKit handles this)
   - Loading states (ChatKit handles this)
   - Error states (ChatKit handles this)
   - Auto-scroll behavior (ChatKit handles this)

2. **Custom Integration Types** (frontend only - minimal)
   - JWT token retrieval function
   - Custom fetch function with authentication
   - ChatKit configuration object
   - Theme styling overrides

3. **AgentRequest** (API contract - existing from Feature 005)
   - Fields: user_id (from JWT), message (user's text input)
   - Validation: user_id required, message 1-1000 chars

4. **AgentResponse** (API contract - existing from Feature 005)
   - Fields: response (agent's text response), metadata (intent, tool_called, confidence, execution_time_ms)
   - Validation: response required, metadata optional

**Key Point**: ChatKit significantly reduces the data model complexity. We don't need custom ChatMessage, ChatSession, or state management entities because ChatKit provides all of this out of the box.

### API Contracts

The following contracts are documented in `contracts/`:

1. **chat-api.json** (Reference existing agent endpoint from Feature 005)
   - Endpoint: POST /api/v1/agent/chat
   - Request: AgentRequest schema
   - Response: AgentResponse schema
   - Errors: 401 (unauthorized), 400 (validation), 500 (server error)
   - **No changes needed** - existing endpoint works with ChatKit

2. **chatkit-integration.json** (ChatKit configuration contract)
   - ChatKit configuration options
   - Custom fetch function signature
   - Theme styling properties
   - Error handling patterns

### Integration Scenarios

The following scenarios are documented in `quickstart.md`:

1. **Happy Path**: User sends message via ChatKit → Agent responds → ChatKit displays response
2. **Create Task**: User types "Create a task to buy milk" → Agent creates task → ChatKit shows confirmation
3. **List Tasks**: User types "Show my tasks" → Agent lists tasks → ChatKit displays formatted list
4. **Complete Task**: User types "Complete task 1" → Agent marks complete → ChatKit shows confirmation
5. **Error Handling**: Network error → ChatKit displays error message → User can retry
6. **Authentication**: Token expired → Custom fetch detects 401 → Redirect to login

**Key Integration Points**:
- ChatKit's `useChatKit` hook with custom fetch
- JWT token injection in custom fetch headers
- Error handling in custom fetch (auth, timeout, network)
- Theme styling via CSS modules or Tailwind
- SSR-safe rendering with Next.js dynamic import

## Phase 2: Task Breakdown

Task breakdown has been generated via `/sp.tasks` command using chatkit-expert agent.

**Task Categories (ChatKit Integration)**:
1. **Setup Tasks**: Install ChatKit package (`@openai/chatkit-react`), install DOMPurify, create chat route
2. **ChatKit Integration Tasks**: Create ChatKitWrapper component, configure ChatKit with custom fetch
3. **Authentication Tasks**: Implement JWT token retrieval, pass token in custom fetch headers
4. **Error Handling Tasks**: Handle auth errors (401), timeout errors (30s), network errors in custom fetch
5. **Styling Tasks**: Extract theme variables, style ChatKit with CSS modules or Tailwind
6. **Testing Tasks**: Test ChatKit integration, test all 5 task operations via chat
7. **Polish Tasks**: Responsive design testing, accessibility, performance validation

**Key Simplifications with ChatKit**:
- ❌ No need to build: Message, MessageList, MessageInput, LoadingIndicator components (ChatKit provides these)
- ❌ No need to implement: Auto-scroll, message rendering optimization, state management (ChatKit handles these)
- ✅ Only need to build: ChatKitWrapper component, custom fetch function, theme styling
- ✅ Focus on: Integration, authentication, error handling, theme consistency

**Total Tasks**: 80 tasks organized by user story (generated by chatkit-expert agent)

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
