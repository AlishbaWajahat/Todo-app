# Data Model: Chat UI & End-to-End Integration

**Feature**: 006-chat-ui-integration
**Date**: 2026-02-09
**Purpose**: Define data structures for chat interface

## Overview

This feature uses **in-memory data structures only** (no database persistence per spec requirements FR-018, FR-019, OOS-001). All entities exist on the frontend during the current session and are destroyed when the user navigates away.

## Frontend Entities (In-Memory)

### 1. ChatMessage

Represents a single message in the chat conversation.

**TypeScript Interface**:
```typescript
interface ChatMessage {
  id: string;                    // UUID v4 (client-generated)
  text: string;                  // Message content (1-1000 chars)
  sender: 'user' | 'agent';      // Message sender
  timestamp: Date;               // When message was created
  status: 'sending' | 'sent' | 'error'; // Message status
}
```

**Field Descriptions**:
- `id`: Unique identifier for React key prop and message tracking
- `text`: Message content, sanitized before storage
- `sender`: Distinguishes user messages from agent responses
- `timestamp`: Used for display and ordering
- `status`: Tracks message lifecycle for UI feedback

**Validation Rules**:
- `id`: Must be valid UUID v4 format
- `text`: Required, 1-1000 characters (enforced on input)
- `sender`: Must be 'user' or 'agent' (enum)
- `timestamp`: Must be valid Date object
- `status`: Must be 'sending', 'sent', or 'error' (enum)

**State Transitions**:
```
User Message:
  [created] → sending → sent
                     ↘ error (if request fails)

Agent Message:
  [created] → sent (agent responses arrive complete)
```

**Example**:
```typescript
const userMessage: ChatMessage = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  text: 'Create a task to buy groceries',
  sender: 'user',
  timestamp: new Date('2026-02-09T10:30:00Z'),
  status: 'sent'
};

const agentMessage: ChatMessage = {
  id: '6ba7b810-9dad-11d1-80b4-00c04fd430c8',
  text: 'Task created: buy groceries',
  sender: 'agent',
  timestamp: new Date('2026-02-09T10:30:02Z'),
  status: 'sent'
};
```

---

### 2. ChatSession

Represents the current chat conversation state.

**TypeScript Interface**:
```typescript
interface ChatSession {
  messages: ChatMessage[];       // Array of all messages in session
  isLoading: boolean;            // True when waiting for agent response
  error: string | null;          // Error message if request failed
}
```

**Field Descriptions**:
- `messages`: Ordered array of messages (oldest first)
- `isLoading`: Controls loading indicator display
- `error`: User-friendly error message (null if no error)

**Validation Rules**:
- `messages`: Must be array (can be empty)
- `isLoading`: Must be boolean
- `error`: Must be string or null

**Lifecycle**:
```
[Page Load] → ChatSession created with empty messages[]
[User sends message] → isLoading = true
[Agent responds] → isLoading = false, new message added
[Error occurs] → isLoading = false, error set
[User navigates away] → ChatSession destroyed
```

**Example**:
```typescript
const session: ChatSession = {
  messages: [
    { id: '...', text: 'Show my tasks', sender: 'user', ... },
    { id: '...', text: 'You have 3 tasks: ...', sender: 'agent', ... }
  ],
  isLoading: false,
  error: null
};
```

---

## Backend Entities (Existing - Reference Only)

### 3. AgentRequest

Request payload sent to agent endpoint (existing from Feature 005).

**Python Schema** (Pydantic):
```python
class AgentRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=1000)
```

**TypeScript Interface** (Frontend):
```typescript
interface AgentRequest {
  user_id: string;               // From JWT token
  message: string;               // User's message (1-1000 chars)
}
```

**Field Descriptions**:
- `user_id`: Authenticated user identifier from JWT token
- `message`: User's natural language message

**Validation Rules**:
- `user_id`: Required, min length 1
- `message`: Required, 1-1000 characters

**Example**:
```typescript
const request: AgentRequest = {
  user_id: 'user-123',
  message: 'Create a task to buy milk'
};
```

---

### 4. AgentResponse

Response payload from agent endpoint (existing from Feature 005).

**Python Schema** (Pydantic):
```python
class AgentResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = None
```

**TypeScript Interface** (Frontend):
```typescript
interface AgentResponse {
  response: string;              // Agent's natural language response
  metadata?: {                   // Optional metadata
    intent: string;              // Classified intent (CREATE, LIST, etc.)
    tool_called: string | null;  // MCP tool that was invoked
    confidence: number;          // Intent classification confidence
    execution_time_ms: number;   // Request execution time
  };
}
```

**Field Descriptions**:
- `response`: Agent's natural language response to display to user
- `metadata`: Optional execution metadata (for debugging/analytics)

**Validation Rules**:
- `response`: Required, non-empty string
- `metadata`: Optional object

**Example**:
```typescript
const response: AgentResponse = {
  response: 'Task created: buy milk',
  metadata: {
    intent: 'CREATE',
    tool_called: 'add_task',
    confidence: 0.95,
    execution_time_ms: 234
  }
};
```

---

## Data Flow

### Message Sending Flow

```
1. User types message in MessageInput
   ↓
2. Frontend creates ChatMessage with status='sending'
   ↓
3. Frontend adds message to ChatSession.messages[]
   ↓
4. Frontend sets ChatSession.isLoading = true
   ↓
5. Frontend sends AgentRequest to POST /api/v1/agent/chat
   ↓
6. Backend processes request (agent → MCP tools → APIs)
   ↓
7. Backend returns AgentResponse
   ↓
8. Frontend updates user message status to 'sent'
   ↓
9. Frontend creates agent ChatMessage from response
   ↓
10. Frontend adds agent message to ChatSession.messages[]
    ↓
11. Frontend sets ChatSession.isLoading = false
    ↓
12. UI auto-scrolls to latest message
```

### Error Handling Flow

```
1. Request fails (network error, timeout, 401, 500)
   ↓
2. Frontend updates user message status to 'error'
   ↓
3. Frontend sets ChatSession.error with user-friendly message
   ↓
4. Frontend sets ChatSession.isLoading = false
   ↓
5. UI displays error message with retry option
   ↓
6. User clicks retry → repeat from step 1
   OR
   User sends new message → clear error, repeat from step 1
```

---

## Persistence Strategy

**No Database Persistence** (per spec requirements):
- Chat messages are NOT stored in database
- Chat history is NOT persisted across sessions
- All data exists in-memory on frontend only
- Data is lost when user navigates away or refreshes page

**Rationale**:
- Spec explicitly requires no chat history persistence (FR-018, OOS-001)
- Stateless design: each request is independent
- Simplifies implementation (no database schema, no migrations)
- Reduces backend complexity and storage costs

**User Experience Implications**:
- Users cannot view previous chat sessions
- Chat history is lost on page refresh
- Users must re-ask questions if they navigate away
- This is acceptable per spec requirements

---

## Security Considerations

### Input Sanitization

**User Input**:
- React automatically escapes text content (no XSS risk)
- Validate length (1-1000 chars) before sending
- No HTML tags allowed (plain text only)

**Agent Response**:
- Sanitize with DOMPurify before storing in ChatMessage
- Strip all HTML tags (ALLOWED_TAGS: [])
- Keep text content only (KEEP_CONTENT: true)

### Authentication

**JWT Token**:
- Retrieved from existing auth system (Feature 002)
- Included in Authorization header for all agent requests
- Never stored in ChatMessage or ChatSession
- Never logged to console

### User Isolation

**Backend Enforcement**:
- Agent endpoint enforces user_id from JWT token
- MCP tools filter all queries by user_id
- Users can only access their own tasks
- Cross-user access returns 404 (not 403 to prevent info leakage)

---

## Performance Considerations

### Message Array Growth

**Problem**: messages[] array grows unbounded during session

**Mitigation**:
- 100 messages is acceptable per spec (no optimization needed)
- If needed: limit to last 200 messages (drop oldest)
- React.memo prevents unnecessary re-renders
- Stable IDs (UUID) optimize React reconciliation

### Memory Management

**Lifecycle**:
- ChatSession created on page mount
- ChatSession destroyed on page unmount
- No memory leaks (no global state, no event listeners)

**Testing**:
- Test with 200 messages to verify performance
- Profile with React DevTools to check re-renders
- Monitor memory usage in browser DevTools

---

## Type Definitions File

**Location**: `frontend/src/types/chat.ts`

```typescript
// frontend/src/types/chat.ts

export type MessageSender = 'user' | 'agent';
export type MessageStatus = 'sending' | 'sent' | 'error';

export interface ChatMessage {
  id: string;
  text: string;
  sender: MessageSender;
  timestamp: Date;
  status: MessageStatus;
}

export interface ChatSession {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}

export interface AgentRequest {
  user_id: string;
  message: string;
}

export interface AgentResponse {
  response: string;
  metadata?: {
    intent: string;
    tool_called: string | null;
    confidence: number;
    execution_time_ms: number;
  };
}

export interface AgentError {
  detail: string;
  code: string;
}
```

---

## Summary

| Entity | Location | Persistence | Purpose |
|--------|----------|-------------|---------|
| ChatMessage | Frontend (in-memory) | Session only | Single message in conversation |
| ChatSession | Frontend (in-memory) | Session only | Current conversation state |
| AgentRequest | API payload | None | Request to agent endpoint |
| AgentResponse | API payload | None | Response from agent endpoint |

**Key Points**:
- All chat data is in-memory on frontend
- No database persistence (per spec requirements)
- Simple data structures (no complex relationships)
- Type-safe with TypeScript interfaces
- Security enforced at API boundary (JWT + user_id)
