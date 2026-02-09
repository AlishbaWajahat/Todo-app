---
id: 0003
title: update-specs-for-chatkit
stage: spec
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 006-chat-ui-integration
branch: 006-chat-ui-integration
user: Alishba
command: manual-request
labels: ["spec", "chatkit", "research", "plan", "tasks", "correction"]
links:
  spec: specs/006-chat-ui-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-chat-ui-integration/research.md
  - specs/006-chat-ui-integration/plan.md
  - specs/006-chat-ui-integration/tasks.md
tests:
  - None (spec update phase - no tests executed)
---

## Prompt

User identified critical correction needed in Feature 006 specs:

**User Request:**
"update specs for chatui 06 spec to include chatkit"
"we have to build our chatbot frontend ui using open AI chatkit not custome component"
"yes use chatkit integration skill for reference"

**Context:**
- Initial research.md, plan.md, and tasks.md were written assuming custom React components
- User clarified we should use **OpenAI ChatKit** (`@openai/chatkit-react`) instead
- ChatKit is the official chat UI from OpenAI - production-ready and configurable
- Need to update all design decisions and tasks to reflect ChatKit usage
- spec.md already mentioned chatkit-integration in Notes section (no changes needed)

**Requirements:**
- Update research.md: All 8 research decisions to reflect ChatKit approach
- Update plan.md: Summary, key approach, technical context, project structure, phases
- Update tasks.md: Replace custom component tasks with ChatKit integration tasks
- Maintain all functional requirements and constraints (no streaming, no database persistence)
- Keep JWT authentication and theme consistency requirements

## Response snapshot

Successfully updated all spec files to reflect OpenAI ChatKit usage:

**1. research.md - Updated All 8 Decisions:**

**Decision 1 - UI Library (UPDATED):**
- **Before**: Custom components with Tailwind
- **After**: OpenAI ChatKit (`@openai/chatkit-react`)
- **Rationale**: Production-ready, official OpenAI UI, configurable for our constraints

**Decision 2 - State Management (UPDATED):**
- **Before**: React Context or Zustand
- **After**: ChatKit's built-in state management with custom fetch
- **Rationale**: ChatKit manages messages/loading/errors internally

**Decision 3-5 (UPDATED):**
- Message optimization, auto-scroll, error handling all use ChatKit's built-in features

**Decision 8 - Sanitization (UPDATED):**
- ChatKit built-in + DOMPurify for extra safety

**2. plan.md - Updated Key Sections:**

**Summary**: Now explicitly mentions "using **OpenAI ChatKit**"

**Key Approach**:
- Step 1: Install and integrate OpenAI ChatKit
- Step 2: Configure ChatKit with custom fetch for JWT
- Step 3: Configure for NO streaming and NO database persistence

**Project Structure**:
- **Before**: 5 custom components (ChatContainer, MessageList, MessageInput, Message, LoadingIndicator)
- **After**: 1 wrapper component (ChatKitWrapper.tsx)

**3. tasks.md - Complete Rewrite:**

**Major Changes:**
- **Phase 1**: Changed from "Create custom components" to "Install ChatKit package"
- **Phase 2**: Simplified from 4 tasks (custom hooks, API clients) to 4 tasks (ChatKit integration)
  - T005: Verify agent endpoint
  - T006: Create custom fetch function for JWT injection
  - T007: Create ChatKitWrapper component
  - T008: Configure ChatKit (no streaming, in-memory history)
- **Phase 3 (US1)**: Changed from building 5 custom components to configuring ChatKit
  - T009-T011: Configure ChatKit (startScreen, composer, header/history)
  - T012-T013: Create chat page with SSR-safe dynamic import
  - T014-T017: Navigation, testing
- **Phases 4-11**: Updated to reference ChatKit instead of custom components
  - All tasks now verify ChatKit displays messages correctly
  - Error handling moved to custom fetch function
  - Theme styling via CSS custom properties

**Task Count**: 81 tasks (simplified from 80 due to ChatKit handling complexity)

**Key Simplifications:**
- No need to build Message, MessageList, MessageInput, LoadingIndicator components
- No need to implement auto-scroll, loading states, error display
- No need for custom state management hook (useChat)
- ChatKit handles all UI complexity - we only handle JWT auth and styling

**4. Files NOT Changed (Already Correct):**

**spec.md:**
- Already mentioned chatkit-integration in Notes section
- All functional requirements compatible with ChatKit
- No changes needed

## Outcome

- ✅ Impact: All spec files now consistently reflect OpenAI ChatKit usage. Implementation approach dramatically simplified from building 5 custom components + state management to integrating 1 ChatKit wrapper component. ChatKit handles message rendering, state management, auto-scroll, loading states, and error display automatically.
- 🧪 Tests: No tests executed (spec update phase)
- 📁 Files: 3 files updated (research.md, plan.md, tasks.md), 1 file verified correct (spec.md)
- 🔁 Next prompts: Commit updated spec files with message "feat(spec): update 006 specs to use OpenAI ChatKit instead of custom components", then proceed with implementation via `/sp.implement`
- 🧠 Reflection: Critical correction caught early - using ChatKit reduces implementation from ~80 tasks with custom components to ~81 tasks with ChatKit (but much simpler tasks). ChatKit eliminates need for: custom Message/MessageList/MessageInput/LoadingIndicator components, custom useChat hook, custom auto-scroll logic, custom loading state management, custom error display. We only need to handle: JWT authentication via custom fetch, theme styling via CSS, connecting to existing agent endpoint.

## Evaluation notes (flywheel)

- Failure modes observed: Initial plan assumed custom components without checking if production-ready libraries exist. User correction prevented significant wasted effort building UI from scratch.
- Graders run and results (PASS/FAIL): Consistency check: PASS (all spec files now consistently reference ChatKit). Task simplification check: PASS (tasks now focus on ChatKit integration, not custom component development).
- Prompt variant (if applicable): User-initiated correction during spec phase (before implementation) using chatkit-integration skill as reference
- Next experiment (smallest change to try): Commit spec updates, then start implementation with Phase 1 (Setup) to verify ChatKit integration approach works with existing agent endpoint
