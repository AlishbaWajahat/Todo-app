# ChatKit Floating Widget Implementation

## Overview
This document describes the floating ChatKit widget implementation for the Todo App. The widget appears on all protected pages and provides AI-powered task management assistance.

## Architecture

### Frontend Components

#### 1. ChatKitWidget Component
**Location:** `frontend/components/chat/ChatKitWidget.tsx`

**Features:**
- Floating chat button in bottom-right corner
- Expandable chat interface (400x600px modal)
- Unread message counter badge
- New conversation functionality
- JWT authentication integration
- Conversation persistence via localStorage
- Dynamic import with SSR disabled

**Key Functions:**
- `getCookie()` - Extracts JWT token from cookies
- `handleSendMessage()` - Sends messages to backend with authentication
- `handleNewConversation()` - Resets conversation state

**State Management:**
- `isOpen` - Widget open/closed state
- `conversationId` - Current conversation UUID
- `unreadCount` - Number of unread messages
- `isReady` - Client-side hydration status

#### 2. Protected Layout Integration
**Location:** `frontend/app/(protected)/layout.tsx`

**Changes:**
- Added dynamic import of ChatKitWidget (SSR disabled)
- Widget appears on all protected pages
- No impact on existing page layouts

### Backend Integration

#### 1. ChatKit Server Utility
**Location:** `backend/chatkit_server.py`

**Purpose:** Utility functions for ChatKit integration

**Key Functions:**
- `convert_to_chatkit_response()` - Converts backend response to ChatKit format
- `extract_conversation_id()` - Extracts UUID from ChatKit metadata
- `format_error_response()` - Formats errors for ChatKit
- `validate_chatkit_message()` - Validates message length and content

**Configuration:**
- `CHATKIT_CONFIG` - ChatKit UI configuration constants
- Max message length: 2000 characters
- Predefined prompts for common tasks
- Theme configuration (blue primary color)

#### 2. Existing Chat Endpoint
**Location:** `backend/api/v1/endpoints/chat.py`

**Already Implemented:**
- POST `/api/v1/chat` endpoint
- JWT authentication via `get_current_user` dependency
- Conversation creation and retrieval
- Message persistence (user + assistant messages)
- Tool call tracking
- Agent integration (Gemini with MCP tools)

**Request Format:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": "uuid-or-null"
}
```

**Response Format:**
```json
{
  "response": "Task created successfully",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "metadata": {
    "intent": "CREATE",
    "tool_called": "add_task",
    "execution_time_ms": 312
  }
}
```

## Authentication Flow

1. User logs in → Better Auth creates session and JWT token
2. JWT token stored in `auth_token` cookie
3. Widget extracts token via `getCookie('auth_token')`
4. Token sent in `Authorization: Bearer <token>` header
5. Backend validates token and identifies user
6. Responses filtered to user's data only

## Conversation Persistence

### Frontend (localStorage)
- Key: `chatkit_widget_conversation_id`
- Value: UUID string
- Persists across page navigation
- Cleared on "New" conversation button

### Backend (PostgreSQL)
- Tables: `conversations`, `messages`, `tool_calls`
- Conversation linked to user via `user_id`
- Messages ordered by `sequence_number`
- Tool calls linked to assistant messages

## User Experience

### Widget States

1. **Closed State:**
   - Floating blue button (bottom-right)
   - Chat bubble icon
   - Unread count badge (if messages received while closed)
   - Hover effect with scale animation

2. **Open State:**
   - 400x600px modal window
   - Blue header with title and controls
   - ChatKit interface with greeting
   - Quick prompt buttons
   - Message input with send button
   - "New" conversation button
   - Close button (X)

### Quick Prompts
- "Add a task" → "Add a task to buy groceries"
- "Show my tasks" → "Show me all my tasks"
- "Complete a task" → "Mark task 1 as complete"
- "Update a task" → "Update task 2 title to 'Buy organic milk'"
- "Delete a task" → "Delete task 3"

## Dependencies

### Frontend
- `@openai/chatkit-react@1.4.3` - ChatKit UI component
- `react-icons@5.5.0` - Icon library (chat bubble, close icons)
- `next@16.0.10` - Next.js framework
- `react@19.2.0` - React library

### Backend
- `fastapi` - Web framework
- `sqlmodel` - ORM for database
- `python-jose` - JWT token handling
- `psycopg2-binary` - PostgreSQL driver

## Environment Variables

### Frontend
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend
```env
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
JWT_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
CORS_ORIGINS=["http://localhost:3000"]
GEMINI_API_KEY=your-gemini-api-key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

## Testing Instructions

### 1. Start Backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test Widget
1. Navigate to any protected page (dashboard, tasks, profile)
2. Click floating chat button (bottom-right)
3. Widget should open with greeting message
4. Try quick prompts or type custom messages
5. Verify responses from AI agent
6. Test "New" conversation button
7. Close and reopen - conversation should persist
8. Navigate to different page - widget should remain available

### 4. Test Authentication
1. Log out and try to access protected page
2. Should redirect to login
3. After login, widget should work with user's tasks

### 5. Test Conversation Persistence
1. Send a message
2. Close widget
3. Refresh page
4. Reopen widget - conversation should be preserved
5. Click "New" - conversation should reset

## File Structure

```
frontend/
├── app/
│   └── (protected)/
│       ├── layout.tsx                    # Modified: Added ChatKitWidget
│       └── chat/
│           └── page.tsx                  # Existing: Full-page chat (optional)
└── components/
    └── chat/
        ├── ChatKitWidget.tsx             # New: Floating widget
        ├── ChatKitWrapper.tsx            # Existing: Full-page wrapper
        └── SimpleChatUI.tsx              # Existing: Custom chat UI

backend/
├── api/
│   └── v1/
│       └── endpoints/
│           └── chat.py                   # Existing: Chat endpoint
├── chatkit_server.py                     # New: ChatKit utilities
├── agent/
│   └── agent.py                          # Existing: AI agent
└── models/
    ├── conversation.py                   # Existing: Conversation model
    ├── message.py                        # Existing: Message model
    └── tool_call.py                      # Existing: Tool call model
```

## Key Features

1. **Always Available:** Widget appears on all protected pages
2. **Persistent Conversations:** Survives page navigation and refresh
3. **Authenticated:** Uses JWT tokens from Better Auth
4. **Real-time:** Immediate responses from AI agent
5. **Task Management:** Full CRUD operations via natural language
6. **Unread Indicators:** Badge shows unread count when closed
7. **Responsive Design:** Fixed size modal with scrollable content
8. **Error Handling:** Graceful error messages for auth/network issues

## Security Considerations

1. **JWT Validation:** All requests validated by backend middleware
2. **User Isolation:** Conversations and tasks filtered by user_id
3. **CORS Protection:** Only allowed origins can access API
4. **Input Validation:** Message length limited to 2000 characters
5. **No Token Exposure:** JWT never logged or exposed in responses
6. **HTTPS Required:** Production should use HTTPS only

## Future Enhancements

1. **Streaming Responses:** Real-time token streaming for longer responses
2. **Voice Input:** Speech-to-text integration
3. **File Attachments:** Upload files for task descriptions
4. **Conversation History:** List and switch between past conversations
5. **Typing Indicators:** Show when agent is processing
6. **Message Reactions:** Like/dislike for response quality
7. **Export Conversations:** Download chat history
8. **Mobile Optimization:** Responsive design for mobile devices

## Troubleshooting

### Widget Not Appearing
- Check browser console for errors
- Verify `@openai/chatkit-react` is installed
- Ensure dynamic import is working (SSR disabled)
- Check if user is authenticated

### Authentication Errors
- Verify JWT_SECRET matches between frontend and backend
- Check if auth_token cookie exists
- Ensure CORS_ORIGINS includes frontend URL
- Verify token hasn't expired

### Conversation Not Persisting
- Check localStorage for `chatkit_widget_conversation_id`
- Verify database connection
- Check backend logs for errors
- Ensure conversation_id is being returned in response

### Agent Not Responding
- Verify GEMINI_API_KEY is set
- Check backend logs for agent errors
- Ensure MCP tools are working
- Test agent endpoint directly

## Support

For issues or questions:
1. Check backend logs: `backend/logs/`
2. Check browser console for frontend errors
3. Verify environment variables are set correctly
4. Test chat endpoint directly with curl/Postman
5. Review database for conversation/message records
