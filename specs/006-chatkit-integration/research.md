# Research: ChatKit UI & End-to-End Integration

**Feature**: 006-chatkit-integration
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document consolidates research findings for integrating OpenAI ChatKit into the existing Next.js frontend and connecting it to the FastAPI backend agent with database-backed conversation persistence.

---

## Research Area 1: ChatKit Integration with Next.js 16 App Router

### Decision: Use ChatKit React Hook with Dynamic Import

**Rationale**:
- ChatKit is a client-side component that requires browser APIs
- Next.js 16 App Router uses Server Components by default
- Must use dynamic import with `ssr: false` to prevent hydration errors

**Implementation Pattern**:

```typescript
// app/(protected)/chat/page.tsx
'use client';

import dynamic from 'next/dynamic';
import { useChatKit } from '@openai/chatkit-react';

const ChatKitWrapper = dynamic(
  () => import('@/components/chat/ChatKitWrapper'),
  { ssr: false }
);

export default function ChatPage() {
  return <ChatKitWrapper />;
}
```

**Key Configuration**:
- `api.url`: Points to FastAPI backend endpoint
- `api.fetch`: Custom fetch function to inject JWT token from Better Auth
- `startScreen.greeting`: Welcome message for new conversations
- `startScreen.prompts`: Suggested prompts for task management
- `theme`: Match existing Tailwind theme (dark mode support)

**Alternatives Considered**:
1. **Build custom chat UI**: Rejected - violates spec requirement to use ChatKit
2. **Use ChatKit CDN script**: Rejected - not compatible with React 19 and TypeScript
3. **Server-side rendering**: Rejected - ChatKit requires browser APIs

**Source**: Context7 documentation for `/openai/openai-chatkit-advanced-samples`

---

## Research Area 2: Conversation Database Schema

### Decision: Three-Table Schema with JSONB for Tool Metadata

**Schema Design**:

```sql
-- conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);

-- messages table
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_conversation_sequence UNIQUE (conversation_id, sequence_number)
);

CREATE INDEX idx_messages_conversation_sequence ON messages(conversation_id, sequence_number);

-- tool_calls table
CREATE TABLE tool_calls (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL,
    tool_input JSONB NOT NULL,
    tool_output JSONB,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'success', 'error')),
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_tool_calls_message_id ON tool_calls(message_id);
CREATE INDEX idx_tool_calls_tool_name ON tool_calls(tool_name);
```

**Rationale**:
- **UUID for conversations**: Prevents enumeration attacks, better for distributed systems
- **BIGSERIAL for messages**: Auto-incrementing, handles high volume
- **sequence_number**: Explicit ordering (more reliable than timestamps)
- **JSONB for tool data**: Flexible storage for tool inputs/outputs, enables querying
- **CASCADE deletes**: Automatic cleanup when user or conversation is deleted
- **Indexes**: Optimized for common queries (user's conversations, conversation history)

**Alternatives Considered**:
1. **Single messages table**: Rejected - harder to manage conversation metadata
2. **Embed tool calls in messages**: Rejected - violates normalization, harder to query
3. **Use MongoDB**: Rejected - constitution requires PostgreSQL

**Source**: Database research from Context7 and PostgreSQL best practices

---

## Research Area 3: Chat Endpoint Design

### Decision: Create New Endpoint `/api/v1/chat` with Conversation Context

**Rationale**:
- Existing `/api/v1/agent/chat` is stateless and doesn't handle conversation history
- New endpoint will wrap existing agent logic with conversation persistence
- Maintains backward compatibility with existing agent endpoint

**Endpoint Specification**:

```python
POST /api/v1/chat
Headers:
  Authorization: Bearer <jwt_token>
  Content-Type: application/json

Request Body:
{
  "message": "Create a task to buy groceries",
  "conversation_id": "uuid-optional"  # null for new conversation
}

Response:
{
  "response": "Task created: Buy groceries",
  "conversation_id": "uuid",
  "metadata": {
    "intent": "CREATE",
    "tool_called": "add_task",
    "confidence": 0.95,
    "execution_time_ms": 312
  }
}
```

**Flow**:
1. Extract user_id from JWT token
2. Load conversation history from database (if conversation_id provided)
3. Append new user message to history
4. Call existing agent.process_request() with user message
5. Save user message and agent response to database
6. Return response with conversation_id

**Alternatives Considered**:
1. **Modify existing agent endpoint**: Rejected - breaks existing API contract
2. **Use ChatKit server SDK**: Rejected - adds unnecessary complexity, we already have agent logic
3. **Store history in Redis**: Rejected - violates stateless architecture requirement

**Source**: FastAPI best practices and existing endpoint patterns

---

## Research Area 4: Session Management Strategy

### Decision: Client-Side Conversation ID with localStorage

**Implementation**:

```typescript
// Frontend: lib/hooks/useChat.ts
const [conversationId, setConversationId] = useState<string | null>(null);

useEffect(() => {
  // Load conversation ID from localStorage
  const savedId = localStorage.getItem('current_conversation_id');
  if (savedId) {
    setConversationId(savedId);
  }
}, []);

const sendMessage = async (message: string) => {
  const response = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId
    })
  });

  const data = await response.json();

  // Save conversation ID for future messages
  if (data.conversation_id) {
    setConversationId(data.conversation_id);
    localStorage.setItem('current_conversation_id', data.conversation_id);
  }

  return data;
};
```

**Rationale**:
- **localStorage**: Persists across browser sessions, survives page refreshes
- **Client-side management**: Backend remains stateless, no session storage needed
- **Automatic creation**: First message creates new conversation, subsequent messages reuse ID
- **User control**: User can start new conversation by clearing localStorage or clicking "New Chat"

**Alternatives Considered**:
1. **Server-side session**: Rejected - violates stateless architecture
2. **URL parameter**: Rejected - poor UX, conversation ID in URL is confusing
3. **Cookies**: Rejected - localStorage is simpler and more explicit

**Source**: ChatKit advanced samples and React state management patterns

---

## Research Area 5: Confirmation Prompts for Destructive Actions

### Decision: Two-Step Confirmation Flow with Agent State

**Implementation Pattern**:

```python
# Backend: agent/agent.py
async def process_request(user_id: str, message: str, conversation_id: str = None) -> AgentResponse:
    # Parse intent
    intent = parse_intent(message)

    # Check if destructive action
    if intent.operation_type == Intent.DELETE:
        # Check if this is a confirmation response
        if message.lower() in ['yes', 'confirm', 'delete']:
            # Execute deletion
            tool_result = await invoke_tool(user_id, intent)
            return format_response(intent, tool_result)
        else:
            # Request confirmation
            return AgentResponse(
                response="⚠️ Are you sure you want to delete this task? Reply 'yes' to confirm or 'no' to cancel.",
                metadata={
                    "intent": "DELETE_CONFIRMATION_REQUIRED",
                    "pending_action": intent.model_dump()
                }
            )

    # Non-destructive actions proceed immediately
    tool_result = await invoke_tool(user_id, intent)
    return format_response(intent, tool_result)
```

**Rationale**:
- **Two-step flow**: Agent asks for confirmation, waits for user response
- **Explicit confirmation**: User must type "yes" or "confirm" to proceed
- **Stateless**: Confirmation state stored in conversation history, not memory
- **Clear messaging**: Warning emoji and explicit instructions

**Destructive Actions Requiring Confirmation**:
- Delete task (single)
- Delete multiple tasks (bulk)
- Clear all completed tasks
- Any operation affecting >1 task

**Alternatives Considered**:
1. **Modal dialog in UI**: Rejected - violates "no manual UI logic outside ChatKit" constraint
2. **Undo functionality**: Rejected - out of scope, adds complexity
3. **No confirmation**: Rejected - violates constitution Principle IX

**Source**: Constitution requirements and UX best practices

---

## Research Area 6: Message Pagination Strategy

### Decision: Load Last 50 Messages Initially, Lazy Load Older Messages

**Implementation**:

```python
# Backend: Load conversation history
def get_conversation_history(conversation_id: str, limit: int = 50, offset: int = 0):
    messages = db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.sequence_number.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()

    # Reverse to get chronological order
    return list(reversed(messages))
```

**Rationale**:
- **50 messages**: Balances context vs performance (typical conversation length)
- **Newest first**: Users care most about recent messages
- **Lazy loading**: Older messages loaded on demand (scroll to top)
- **Agent context**: Agent receives full history for context (no pagination in agent logic)

**Alternatives Considered**:
1. **Load all messages**: Rejected - poor performance for long conversations
2. **Cursor-based pagination**: Rejected - offset-based is simpler for this use case
3. **Client-side pagination**: Rejected - server should control data access

**Source**: Chat application best practices and performance optimization

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Frontend Integration** | ChatKit with dynamic import, custom fetch for JWT | SSR compatibility, auth integration |
| **Database Schema** | 3 tables (conversations, messages, tool_calls) with JSONB | Normalization, flexibility, performance |
| **Chat Endpoint** | New `/api/v1/chat` wrapping existing agent | Backward compatibility, conversation persistence |
| **Session Management** | Client-side conversation ID in localStorage | Stateless backend, survives page refresh |
| **Confirmation Prompts** | Two-step flow with explicit user confirmation | Safety, constitution compliance |
| **Message Pagination** | Load last 50, lazy load older | Performance, user experience |

---

## Implementation Dependencies

**Frontend**:
- @openai/chatkit-react: 1.4.3 (already installed)
- Better Auth JWT token extraction
- localStorage API

**Backend**:
- SQLModel for new conversation models
- Alembic for database migration
- Existing agent and MCP tools (no changes needed)

**Database**:
- PostgreSQL UUID extension (gen_random_uuid)
- JSONB support (native in PostgreSQL 9.4+)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ChatKit SSR hydration errors | High | Use dynamic import with ssr: false |
| Long conversation performance | Medium | Implement pagination, load last 50 messages |
| Confirmation flow confusion | Medium | Clear messaging, explicit instructions |
| Database migration failure | High | Test migration on Neon branch first |
| JWT token expiration during chat | Medium | Implement token refresh in frontend |

---

## Next Steps

1. **Phase 1: Design & Contracts**
   - Create data-model.md with SQLModel definitions
   - Create API contract for /api/v1/chat endpoint
   - Create quickstart.md with setup instructions

2. **Phase 2: Implementation** (via /sp.tasks)
   - Database migration for conversation tables
   - Backend chat endpoint with conversation persistence
   - Frontend ChatKit integration with JWT auth
   - Confirmation prompt logic in agent
   - End-to-end testing

---

**Research Complete**: All unknowns resolved. Ready for Phase 1: Design & Contracts.
