# ChatKit Integration Setup Guide

## Overview

This guide explains how to use the OpenAI ChatKit integration with your custom FastAPI backend. The integration maintains all your existing agent logic, database models, and authentication while providing a professional chat UI.

## Architecture

### Frontend (Next.js)
- **Component**: `frontend/components/chat/ChatKitWidget.tsx`
- **Library**: `@openai/chatkit-react` v1.4.3
- **Features**: Floating widget, JWT auth, session persistence

### Backend (FastAPI)
- **Adapter**: `backend/api/v1/endpoints/chatkit.py`
- **Bridge**: Translates ChatKit protocol → Existing agent
- **Preserves**: All Conversation, Message, ToolCall models

### Data Flow
```
User → ChatKit UI → Custom Fetch (JWT) → /api/v1/chatkit
  → ChatKit Adapter → Existing Agent (process_request)
  → Database (Conversation, Message, ToolCall) → Response
```

## What Was Changed

### Frontend Changes

**1. ChatKitWidget.tsx** (Replaced)
- **Before**: Custom React chat component with manual UI
- **After**: OpenAI ChatKit library integration
- **Preserved**: JWT authentication, conversation persistence, localStorage

**Key Features**:
```typescript
- Custom fetch with JWT from 'auth_token' cookie
- Conversation ID persistence in localStorage
- Floating widget (bottom-right, 24px offset)
- Blue theme (#2563eb) matching your design
- Quick prompts for common tasks
```

**2. layout.tsx** (Updated)
- Added ChatKit CSS import: `import "@openai/chatkit-react/styles.css";`

**3. ClientLayoutWrapper.tsx** (No changes needed)
- Already configured to load ChatKitWidget dynamically

### Backend Changes

**1. chatkit.py** (New file)
- **Location**: `backend/api/v1/endpoints/chatkit.py`
- **Purpose**: Bridge ChatKit protocol to existing agent

**Key Functions**:
```python
@router.post("/chatkit")
async def chatkit_endpoint():
    # 1. Extract JWT and validate user
    # 2. Parse ChatKit messages array
    # 3. Get/create conversation (existing logic)
    # 4. Save user message (existing Message model)
    # 5. Call process_request() (existing agent)
    # 6. Save assistant message + tool calls
    # 7. Return ChatKit-compatible response
```

**2. main.py** (Updated)
- Added import: `from api.v1.endpoints import chatkit`
- Added router: `app.include_router(chatkit.router, prefix="/api/v1")`

**3. __init__.py** (Updated)
- Added chatkit to exports

## What Was Preserved

### ✅ All Existing Backend Logic
- `agent/agent.py` - No changes
- `agent/intent_parser.py` - No changes
- `agent/response_formatter.py` - No changes
- All MCP tools - No changes

### ✅ All Database Models
- `Conversation` model - No changes
- `Message` model - No changes
- `ToolCall` model - No changes
- All relationships - No changes

### ✅ Authentication
- JWT token validation - No changes
- `get_current_user` dependency - No changes
- Cookie-based auth - No changes

### ✅ Conversation Persistence
- Same conversation ID logic
- Same sequence numbering
- Same localStorage strategy

## How to Use

### 1. Start the Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

### 3. Test the Integration

**Open your browser**: http://localhost:3000

**Log in** with your credentials

**Look for the blue chat button** in the bottom-right corner

**Click it** to open the ChatKit widget

**Try these prompts**:
- "Add a task to buy groceries"
- "Show me all my tasks"
- "Mark task 1 as complete"
- "Update task 2 title to 'Buy organic milk'"

## API Endpoints

### ChatKit Endpoint
```
POST /api/v1/chatkit
Authorization: Bearer <jwt_token>
X-Conversation-Id: <uuid> (optional)

Request Body (ChatKit format):
{
  "messages": [
    {"role": "user", "content": "Add a task to buy groceries"}
  ],
  "stream": false
}

Response (ChatKit format):
{
  "id": "message_id",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "task-assistant",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Task created: Buy groceries"
      },
      "finish_reason": "stop"
    }
  ]
}

Headers:
X-Conversation-Id: <uuid>
```

### Original Chat Endpoint (Still Available)
```
POST /api/v1/chat
Authorization: Bearer <jwt_token>

Request Body:
{
  "message": "Add a task to buy groceries",
  "conversation_id": "uuid or null"
}

Response:
{
  "response": "Task created: Buy groceries",
  "conversation_id": "uuid",
  "metadata": {
    "intent": "CREATE",
    "tool_called": "add_task",
    "execution_time_ms": 312
  }
}
```

## Configuration Options

### Frontend Customization

Edit `frontend/components/chat/ChatKitWidget.tsx`:

```typescript
// Change widget position
overlay: {
  enabled: true,
  position: 'bottom-right', // or 'bottom-left', 'top-right', 'top-left'
  offset: { x: 24, y: 24 },
}

// Change theme colors
theme: {
  primaryColor: '#2563eb', // Change to your brand color
  backgroundColor: '#ffffff',
  textColor: '#111827',
}

// Change greeting and prompts
startScreen: {
  greeting: 'Your custom greeting here',
  prompts: [
    { label: 'Custom prompt 1', prompt: 'Your prompt text' },
    // Add more prompts
  ],
}

// Change header
header: {
  enabled: true,
  title: 'Your Custom Title',
}
```

### Backend Customization

Edit `backend/api/v1/endpoints/chatkit.py`:

```python
# Enable streaming responses
if chatkit_request.stream:
    return StreamingResponse(...)

# Adjust streaming speed
await asyncio.sleep(0.05)  # Change delay between words

# Customize response format
# All responses go through your existing agent
# Modify agent/response_formatter.py to change output
```

## Troubleshooting

### Issue: ChatKit widget not appearing

**Solution**:
1. Check browser console for errors
2. Verify `@openai/chatkit-react` is installed: `npm list @openai/chatkit-react`
3. Ensure you're on a protected route (logged in)
4. Check that CSS is imported in `layout.tsx`

### Issue: Authentication errors

**Solution**:
1. Check that JWT token exists in cookies: `document.cookie`
2. Verify token is named 'auth_token'
3. Check backend logs for authentication failures
4. Ensure `/api/v1/chatkit` is not bypassed by auth middleware

### Issue: Conversation not persisting

**Solution**:
1. Check localStorage: `localStorage.getItem('chatkit_widget_conversation_id')`
2. Verify conversation ID is returned in response headers
3. Check database for conversation records
4. Ensure conversation_id is passed in subsequent requests

### Issue: Agent not responding correctly

**Solution**:
1. Test the original `/api/v1/chat` endpoint directly
2. Check backend logs for agent errors
3. Verify MCP tools are working
4. Test agent logic independently

### Issue: CORS errors

**Solution**:
1. Verify `CORS_ORIGINS` in backend `.env`
2. Check that frontend URL is in allowed origins
3. Ensure credentials are allowed in CORS config
4. Check browser network tab for preflight requests

## Streaming Support

The ChatKit adapter supports streaming responses:

```typescript
// Frontend: ChatKit automatically handles streaming
// No changes needed in ChatKitWidget.tsx

// Backend: Enable streaming in request
{
  "messages": [...],
  "stream": true  // Enable streaming
}
```

**Streaming behavior**:
- Words are streamed one at a time
- 50ms delay between words (configurable)
- Uses Server-Sent Events (SSE)
- ChatKit handles UI updates automatically

## Database Schema

No changes to existing schema. ChatKit adapter uses:

```sql
-- Conversations table (existing)
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Messages table (existing)
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL,
    role VARCHAR NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP,
    model VARCHAR(100),
    tokens_used INTEGER
);

-- Tool calls table (existing)
CREATE TABLE tool_calls (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL,
    tool_name VARCHAR NOT NULL,
    tool_input JSONB,
    tool_output JSONB,
    status VARCHAR NOT NULL,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

## Performance Considerations

### Frontend
- ChatKit widget loads dynamically (no SSR)
- Conversation ID cached in localStorage
- JWT token read from cookies (no API call)

### Backend
- Same performance as original `/api/v1/chat`
- No additional database queries
- Agent logic unchanged
- Streaming adds minimal overhead

## Security

### Authentication
- ✅ JWT validation on every request
- ✅ User isolation enforced
- ✅ Conversation ownership verified
- ✅ No token exposure in URLs

### Data Protection
- ✅ All messages stored in database
- ✅ User can only access own conversations
- ✅ Tool calls logged for audit
- ✅ CORS properly configured

## Next Steps

1. **Test the integration** - Try all task operations through ChatKit
2. **Customize the UI** - Adjust colors, prompts, and positioning
3. **Monitor performance** - Check response times and database queries
4. **Add features** - Consider adding file uploads, voice input, etc.
5. **Deploy** - Follow your existing deployment process

## Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review backend logs: `backend/logs/`
3. Check browser console for frontend errors
4. Test the original `/api/v1/chat` endpoint
5. Verify database connectivity

## Summary

✅ **ChatKit UI integrated** - Professional chat interface
✅ **Backend preserved** - All existing agent logic intact
✅ **Database unchanged** - Same models and relationships
✅ **Auth maintained** - JWT token validation working
✅ **Conversations persist** - Same localStorage + database strategy
✅ **Streaming supported** - Optional real-time responses
✅ **Production ready** - Error handling and security in place

Your ChatKit integration is complete and ready to use!
