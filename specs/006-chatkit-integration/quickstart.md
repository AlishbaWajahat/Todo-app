# Quickstart: ChatKit UI & End-to-End Integration

**Feature**: 006-chatkit-integration
**Date**: 2026-02-09
**Status**: Draft

## Overview

This guide provides step-by-step instructions for setting up and testing the ChatKit integration with conversation persistence.

---

## Prerequisites

**Backend**:
- Python 3.11+
- PostgreSQL (Neon Serverless)
- Existing backend running on `http://localhost:8000`
- Environment variables configured (`.env` file)

**Frontend**:
- Node.js 18+
- npm or yarn
- Existing frontend running on `http://localhost:3000`

**Required Environment Variables**:
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@host/database
JWT_SECRET=your-jwt-secret-min-32-chars
GEMINI_API_KEY=your-gemini-api-key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
CORS_ORIGINS=["http://localhost:3000"]
```

---

## Step 1: Database Migration

**Run Alembic migration to create conversation tables**:

```bash
cd backend

# Generate migration (if not already created)
alembic revision --autogenerate -m "add_conversation_tables"

# Review migration file in alembic/versions/
# Ensure it creates: conversations, messages, tool_calls tables

# Apply migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: users, tasks, conversations, messages, tool_calls
```

**Verify Schema**:
```sql
-- Check conversations table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'conversations';

-- Check messages table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'messages';

-- Check tool_calls table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'tool_calls';
```

---

## Step 2: Backend Implementation

**Create new models** (`backend/models/conversation.py`, `message.py`, `tool_call.py`):
- Copy SQLModel definitions from `data-model.md`
- Add to `backend/models/__init__.py`

**Create chat endpoint** (`backend/api/v1/endpoints/chat.py`):
- Implement POST `/api/v1/chat` endpoint
- Load conversation history from database
- Call existing `agent.process_request()`
- Save messages and tool calls to database
- Return response with conversation_id

**Update main.py**:
```python
from api.v1.endpoints import chat

app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
```

**Test Backend**:
```bash
# Start backend
cd backend
uvicorn main:app --reload --port 8000

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to buy groceries", "conversation_id": null}'

# Expected response:
# {
#   "response": "Task created: Buy groceries",
#   "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
#   "metadata": {...}
# }
```

---

## Step 3: Frontend Implementation

**Install dependencies** (already installed):
```bash
cd frontend
npm install @openai/chatkit-react
# Already in package.json: "@openai/chatkit-react": "^1.4.3"
```

**Create chat components**:

1. **ChatKitWrapper** (`frontend/components/chat/ChatKitWrapper.tsx`):
```typescript
'use client';

import { useChatKit } from '@openai/chatkit-react';
import { useAuth } from '@/lib/hooks/useAuth';
import { useState, useEffect, useCallback } from 'react';

export default function ChatKitWrapper() {
  const { session } = useAuth();
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Load conversation ID from localStorage
  useEffect(() => {
    const savedId = localStorage.getItem('current_conversation_id');
    if (savedId) setConversationId(savedId);
  }, []);

  // Custom fetch with JWT token
  const customFetch = useCallback(
    async (url: string, options: RequestInit = {}) => {
      const headers = {
        ...options.headers,
        'Authorization': `Bearer ${session?.accessToken}`,
        'Content-Type': 'application/json',
      };
      return fetch(url, { ...options, headers });
    },
    [session]
  );

  const chatkit = useChatKit({
    api: {
      url: 'http://localhost:8000/api/v1/chat',
      fetch: customFetch,
    },
    theme: {
      colorScheme: 'dark',
      radius: 'round',
    },
    startScreen: {
      greeting: 'Welcome! How can I help you manage your tasks today?',
      prompts: [
        'Create a task to buy groceries',
        'Show me my tasks',
        'Mark task 1 as complete',
      ],
    },
    header: { enabled: false },
    history: { enabled: true },
  });

  return <div className="h-full w-full">{chatkit.control}</div>;
}
```

2. **Chat Page** (`frontend/app/(protected)/chat/page.tsx`):
```typescript
'use client';

import dynamic from 'next/dynamic';

const ChatKitWrapper = dynamic(
  () => import('@/components/chat/ChatKitWrapper'),
  { ssr: false }
);

export default function ChatPage() {
  return (
    <div className="h-screen w-full">
      <ChatKitWrapper />
    </div>
  );
}
```

3. **Chat API Client** (`frontend/lib/api/chat.ts`):
```typescript
import { apiClient } from './client';

export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  metadata?: {
    intent: string;
    tool_called: string | null;
    confidence: number;
    execution_time_ms: number;
  };
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/chat', request);
  return response.data;
}

export async function listConversations() {
  const response = await apiClient.get('/conversations');
  return response.data;
}

export async function getConversationMessages(conversationId: string) {
  const response = await apiClient.get(`/conversations/${conversationId}/messages`);
  return response.data;
}
```

**Update Navigation** (`frontend/components/layout/Header.tsx`):
```typescript
// Add chat link to navigation
<Link href="/chat" className="nav-link">
  Chat
</Link>
```

---

## Step 4: Testing

**Test Flow**:

1. **Start Backend**:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. **Start Frontend**:
```bash
cd frontend
npm run dev
```

3. **Login**:
- Navigate to `http://localhost:3000/signin`
- Sign in with existing account

4. **Open Chat**:
- Navigate to `http://localhost:3000/chat`
- Should see ChatKit interface with welcome message

5. **Test Task Creation**:
- Type: "Create a task to buy groceries"
- Expected: "Task created: Buy groceries"
- Verify task appears in database

6. **Test Task Listing**:
- Type: "Show me my tasks"
- Expected: List of all user's tasks

7. **Test Task Completion**:
- Type: "Mark task 1 as complete"
- Expected: "Task marked as complete"

8. **Test Conversation Persistence**:
- Refresh page
- Previous messages should still be visible
- Continue conversation seamlessly

9. **Test Server Restart**:
- Stop backend (Ctrl+C)
- Restart backend
- Refresh frontend
- Conversation history should still be intact

---

## Step 5: Verification Checklist

**Backend Verification**:
- [ ] Database migration applied successfully
- [ ] Conversations table exists with correct schema
- [ ] Messages table exists with correct schema
- [ ] Tool_calls table exists with correct schema
- [ ] POST /api/v1/chat endpoint responds correctly
- [ ] JWT authentication works
- [ ] Conversation history persists in database
- [ ] Tool calls are recorded in database

**Frontend Verification**:
- [ ] ChatKit component renders without errors
- [ ] JWT token is included in API requests
- [ ] Messages are sent and received correctly
- [ ] Conversation ID is stored in localStorage
- [ ] Page refresh preserves conversation
- [ ] New conversation can be started
- [ ] Theme matches existing application

**End-to-End Verification**:
- [ ] User can create tasks via chat
- [ ] User can list tasks via chat
- [ ] User can complete tasks via chat
- [ ] User can update tasks via chat
- [ ] User can delete tasks via chat (with confirmation)
- [ ] Conversation survives server restart
- [ ] Conversation survives browser refresh
- [ ] Multiple users have isolated conversations

---

## Troubleshooting

**Issue: ChatKit not rendering**
- **Cause**: SSR hydration error
- **Solution**: Ensure dynamic import with `ssr: false`

**Issue: 401 Unauthorized**
- **Cause**: JWT token not included or expired
- **Solution**: Check `customFetch` implementation, verify token in localStorage

**Issue: Conversation not persisting**
- **Cause**: conversation_id not saved to localStorage
- **Solution**: Verify `setConversationId` and `localStorage.setItem` are called

**Issue: Database connection error**
- **Cause**: DATABASE_URL incorrect or database not accessible
- **Solution**: Verify DATABASE_URL in .env, check Neon dashboard

**Issue: Tool calls not working**
- **Cause**: Agent not invoking MCP tools
- **Solution**: Check agent logs, verify MCP tools are registered

**Issue: CORS error**
- **Cause**: Frontend origin not in CORS_ORIGINS
- **Solution**: Add `http://localhost:3000` to CORS_ORIGINS in backend .env

---

## Development Tips

**View Database Records**:
```sql
-- View conversations
SELECT * FROM conversations WHERE user_id = 1;

-- View messages for a conversation
SELECT * FROM messages
WHERE conversation_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY sequence_number;

-- View tool calls
SELECT tc.* FROM tool_calls tc
JOIN messages m ON tc.message_id = m.id
WHERE m.conversation_id = '550e8400-e29b-41d4-a716-446655440000';
```

**Clear Conversation**:
```typescript
// In browser console
localStorage.removeItem('current_conversation_id');
location.reload();
```

**Backend Logs**:
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug
```

**Frontend Logs**:
```typescript
// Add to ChatKitWrapper
onError: ({ error }) => {
  console.error('ChatKit error:', error);
}
```

---

## Next Steps

After successful setup:

1. **Add Confirmation Prompts**: Implement two-step confirmation for delete operations
2. **Add Conversation List**: Create sidebar to view and switch between conversations
3. **Add New Conversation Button**: Allow users to start fresh conversations
4. **Optimize Performance**: Add pagination for long conversations
5. **Add Analytics**: Track tool usage and conversation metrics
6. **Deploy to Production**: Configure production environment variables

---

## Production Deployment

**Backend (Render/Railway)**:
```bash
# Set environment variables
DATABASE_URL=<neon-production-url>
JWT_SECRET=<production-secret>
GEMINI_API_KEY=<production-key>
CORS_ORIGINS=["https://yourdomain.com"]

# Deploy
git push production main
```

**Frontend (Vercel)**:
```bash
# Set environment variables
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Deploy
vercel deploy --prod
```

**Database (Neon)**:
- Create production branch
- Run migrations on production database
- Enable connection pooling

---

**Status**: Ready for implementation via `/sp.tasks` command.
