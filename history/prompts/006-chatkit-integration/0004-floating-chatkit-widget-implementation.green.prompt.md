---
id: 0004
title: Floating ChatKit Widget Implementation
stage: green
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: 006-chatkit-integration
branch: 006-chatkit-integration
user: Alishba
command: implementation
labels: ["chatkit", "floating-widget", "ui", "frontend", "backend", "integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/components/chat/ChatKitWidget.tsx
  - frontend/app/(protected)/layout.tsx
  - backend/chatkit_server.py
  - docs/CHATKIT_WIDGET_IMPLEMENTATION.md
  - CHATKIT_QUICKSTART.md
tests:
  - Manual testing required for widget visibility
  - Authentication flow testing
  - Conversation persistence testing
---

## Prompt

Build a floating chatbot interface using OpenAI ChatKit that appears as a widget on all pages of the app.

**Requirements:**

1. **Frontend - Floating ChatKit Widget:**
   - Create a floating chatbot icon (bottom-right corner) that opens/closes the chat interface
   - Use @openai/chatkit-react v1.4.3
   - Widget should be available on all protected pages
   - Should NOT be a separate /chat route - it's a floating widget
   - Implement in frontend/components/chat/ChatKitWidget.tsx
   - Add to the main layout so it appears everywhere

2. **Backend - ChatKit Server Integration:**
   - Create backend/chatkit_server.py to handle ChatKit-specific integration
   - This should wrap the existing chat endpoint logic
   - Handle ChatKit message format conversion
   - Integrate with existing agent (backend/agent/agent.py)
   - Use existing conversation persistence (conversations, messages, tool_calls tables)

3. **Authentication & Persistence:**
   - JWT token from cookies (auth_token)
   - Conversation ID stored in localStorage
   - Connect to existing POST /api/v1/chat endpoint OR create ChatKit-specific endpoint if needed

4. **Current Backend Context:**
   - Existing endpoint: POST /api/v1/chat
   - Request: { message: string, conversation_id: UUID | null }
   - Response: { response: string, conversation_id: UUID, metadata: object }
   - Agent uses Gemini (not Claude) with MCP tools for task management

**Files to Create/Modify:**
- backend/chatkit_server.py (new)
- frontend/components/chat/ChatKitWidget.tsx (new - floating widget, not full page)
- frontend/app/(protected)/layout.tsx (add widget to layout)
- Remove or repurpose frontend/app/(protected)/chat/page.tsx if it exists

Please implement a proper ChatKit floating chatbot widget with backend integration.

## Response snapshot

Successfully implemented a floating ChatKit widget with the following components:

**1. Frontend - ChatKitWidget Component (frontend/components/chat/ChatKitWidget.tsx)**
- Floating blue button (56x56px) in bottom-right corner with chat bubble icon
- Expandable modal (400x600px) with ChatKit interface
- Unread message counter badge
- JWT authentication via cookie extraction
- Conversation persistence using localStorage (key: chatkit_widget_conversation_id)
- New conversation functionality
- Dynamic import with SSR disabled
- Uses react-icons for UI elements (IoChatbubbleEllipsesOutline, IoClose)

**2. Layout Integration (frontend/app/(protected)/layout.tsx)**
- Added dynamic import of ChatKitWidget with SSR disabled
- Widget now appears on all protected pages (dashboard, tasks, profile, etc.)
- No impact on existing page layouts

**3. Backend Utility (backend/chatkit_server.py)**
- Utility functions for ChatKit integration:
  - convert_to_chatkit_response() - Format conversion
  - extract_conversation_id() - UUID extraction from metadata
  - format_error_response() - Error formatting
  - validate_chatkit_message() - Input validation (max 2000 chars)
- CHATKIT_CONFIG constants for UI configuration
- Pydantic models for type safety

**4. Documentation**
- docs/CHATKIT_WIDGET_IMPLEMENTATION.md - Complete technical documentation
- CHATKIT_QUICKSTART.md - Quick start guide for testing

**Key Features Implemented:**
- Always available on all protected pages
- Persistent conversations across page navigation
- JWT authentication integration
- Unread message counter
- Quick prompt buttons for common tasks
- Responsive modal design
- Error handling for auth/network issues
- Integration with existing backend endpoint (no changes needed)

**Technical Details:**
- Uses existing POST /api/v1/chat endpoint
- No backend endpoint changes required
- Conversation persistence via PostgreSQL (existing tables)
- Client-side state management with React hooks
- Dynamic import to avoid SSR issues with browser APIs

## Outcome

- ✅ Impact: Floating ChatKit widget now available on all protected pages with full authentication, persistence, and AI agent integration
- 🧪 Tests: Manual testing required - widget visibility, authentication flow, conversation persistence, agent responses, error handling
- 📁 Files: Created 3 new files (ChatKitWidget.tsx, chatkit_server.py, 2 docs), modified 1 file (layout.tsx)
- 🔁 Next prompts: Test widget on all pages, verify conversation persistence, test error scenarios, mobile responsiveness testing
- 🧠 Reflection: Implementation leveraged existing backend infrastructure effectively. No changes to chat endpoint needed. Widget design follows modern UI patterns with floating button and modal interface.

## Evaluation notes (flywheel)

- Failure modes observed: None during implementation. Potential issues: SSR hydration (mitigated with dynamic import), JWT token expiry (handled by backend), localStorage limits (unlikely with UUID storage)
- Graders run and results (PASS/FAIL): Not applicable - manual testing required
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add typing indicators, implement streaming responses, or add conversation history sidebar
