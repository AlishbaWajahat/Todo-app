# ChatKit Integration - Quick Start

## What You Got

✅ **OpenAI ChatKit UI** integrated with your custom FastAPI backend
✅ **All existing logic preserved** - agent, database, authentication
✅ **Zero breaking changes** - original `/api/v1/chat` still works
✅ **Production ready** - error handling, streaming, persistence

## Start Using It Now

### 1. Start Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test ChatKit
1. Open http://localhost:3000
2. Log in with your credentials
3. Look for **blue chat button** (bottom-right corner)
4. Click to open ChatKit widget
5. Try: **"Add a task to buy groceries"**

## What Changed

### Frontend Files
- `components/chat/ChatKitWidget.tsx` - Replaced with ChatKit library
- `app/layout.tsx` - Added ChatKit CSS import

### Backend Files (NEW)
- `api/v1/endpoints/chatkit.py` - ChatKit adapter endpoint
- `api/v1/endpoints/__init__.py` - Exports chatkit module
- `main.py` - Registers chatkit router

### What Was NOT Changed
- ✅ `agent/agent.py` - All agent logic intact
- ✅ `models/conversation.py` - Database models unchanged
- ✅ `models/message.py` - Database models unchanged
- ✅ `models/tool_call.py` - Database models unchanged
- ✅ `dependencies/auth.py` - JWT auth unchanged
- ✅ All MCP tools - Unchanged

## How It Works

```
User Message → ChatKit UI → JWT Auth → /api/v1/chatkit
  → ChatKit Adapter → Your Existing Agent (process_request)
  → Database (Conversation, Message, ToolCall) → Response
```

**Key Point**: ChatKit adapter is just a protocol translator. Your entire backend logic runs exactly as before.

## API Endpoints

### NEW: ChatKit Endpoint
```
POST /api/v1/chatkit
Authorization: Bearer <jwt_token>
X-Conversation-Id: <uuid>

Body: {"messages": [{"role": "user", "content": "Add a task"}]}
```

### STILL WORKS: Original Endpoint
```
POST /api/v1/chat
Authorization: Bearer <jwt_token>

Body: {"message": "Add a task", "conversation_id": "uuid"}
```

## Customization

Edit `frontend/components/chat/ChatKitWidget.tsx`:

```typescript
// Change position
overlay: { position: 'bottom-right', offset: { x: 24, y: 24 } }

// Change colors
theme: { primaryColor: '#2563eb', backgroundColor: '#ffffff' }

// Change greeting
startScreen: { greeting: 'Your custom greeting' }
```

## Troubleshooting

**Widget not appearing?**
- Check browser console for errors
- Verify you're logged in
- Check: `npm list @openai/chatkit-react`

**Auth errors?**
- Check cookie: `document.cookie` (should have 'auth_token')
- Test original endpoint: `POST /api/v1/chat`

**Agent not working?**
- Check backend logs
- Verify MCP tools are working
- Test agent independently

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Blue chat button appears
- [ ] Widget opens when clicked
- [ ] Can send messages
- [ ] Agent responds correctly
- [ ] Tasks are created/listed/updated
- [ ] Conversation persists after refresh

## Documentation

- **Full Setup Guide**: `CHATKIT_SETUP.md`
- **Architecture Details**: See CHATKIT_SETUP.md
- **API Reference**: See CHATKIT_SETUP.md

## Summary

**Status**: ✅ Ready to use
**Breaking Changes**: None
**Migration Required**: None
**Dependencies**: Already installed

Your ChatKit integration is complete. The widget will appear on all protected pages with full task management capabilities through your existing agent backend.
