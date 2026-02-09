---
name: "chatkit-integration-expert"
description: "Integrate OpenAI ChatKit chatbot UI into any existing web project and connect it to your backend. Supports React, Next.js, Docusaurus, Gatsby, and plain HTML. Includes session management, selected-text questioning, streaming responses, and database persistence. Works with any AI backend (OpenAI, Anthropic, RAG systems, custom agents)."
version: "1.0.0"
---

# ChatKit Integration Expert Skill

## When to Use This Skill

- User wants to "add ChatKit to my website"
- User asks to "integrate a chatbot UI", "add OpenAI ChatKit", or "connect ChatKit to my backend"
- User has an existing AI backend and needs a professional chat interface
- User wants to replace an existing chat UI with ChatKit
- User needs features like selected-text questioning, session persistence, or streaming responses
- User wants a production-ready chat widget with minimal setup

## What This Skill Does

This skill integrates OpenAI ChatKit (the official chat UI from OpenAI) into your existing project and connects it to your backend. Unlike building a chatbot from scratch, this focuses on the **UI integration layer**.

### Key Capabilities

1. **Frontend Integration** - Add ChatKit to any framework (React, Next.js, Docusaurus, Gatsby, Vite)
2. **Backend Connection** - Connect ChatKit to your existing FastAPI/Express/Django backend
3. **Advanced Features** - Session management, selected-text questioning, streaming responses
4. **Database Setup** - PostgreSQL/MongoDB/SQLite for chat history persistence
5. **Production Ready** - Error handling, CORS, monitoring, deployment configs

## Full Deliverables Generated

When you invoke this skill, you get:

### Frontend Files
- `src/components/ChatKitBot/index.jsx` - Main ChatKit component
- `src/components/ChatKitBot/styles.module.css` - Custom styling (optional)
- `src/theme/Root.js` (Docusaurus) or `_app.js` (Next.js) - Global integration
- Configuration updates for your framework

### Backend Files
- `backend/chatkit_server.py` - FastAPI server with ChatKit endpoint
- `backend/chatkit_store.py` - Custom store implementation for database
- `backend/database.py` - Database schema (sessions + messages)
- `backend/requirements.txt` - Python dependencies
- `backend/.env.example` - Environment variables template

### Documentation
- `CHATKIT_SETUP.md` - Complete setup instructions
- `CHATKIT_DEPLOYMENT.md` - Production deployment guide
- `CHATKIT_TROUBLESHOOTING.md` - Common issues and solutions

### Testing Files
- `src/components/ChatKitBot/ChatKitBot.test.jsx` - Frontend tests
- `backend/test_chatkit_server.py` - Backend tests

## How This Skill Works

### Phase 1: Discovery (Automatic)
1. Detect your project framework (React, Next.js, Docusaurus, etc.)
2. Identify your backend technology (FastAPI, Express, Django, etc.)
3. Check for existing database setup
4. Detect your AI backend (OpenAI, Anthropic, RAG, custom)

### Phase 2: Frontend Integration
1. Install `@openai/chatkit-react` package
2. Generate ChatKit component with custom fetch
3. Add session management with localStorage
4. Implement selected-text detection (optional)
5. Configure SSR-safe rendering
6. Add to global layout (Root.js, _app.js, etc.)

### Phase 3: Backend Setup
1. Install `openai-chatkit` Python package
2. Create ChatKit endpoint handler
3. Implement custom store for database persistence
4. Add CORS configuration
5. Connect to your existing AI backend
6. Set up streaming responses

### Phase 4: Testing & Deployment
1. Generate test files
2. Provide deployment configurations
3. Create monitoring setup
4. Document troubleshooting steps

## Example Usage

### Scenario 1: Add ChatKit to Docusaurus Site

**User Input:**
```
Add ChatKit to my Docusaurus documentation site. I have a FastAPI backend at /api/chat that uses OpenAI. I want selected-text questioning and chat history.
```

**What You Get:**

1. **Frontend Component** (`src/components/ChatKitBot/index.jsx`):
```javascript
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useChatKit } from '@openai/chatkit-react';

export default function ChatKitBot() {
  const [sessionId, setSessionId] = useState('');
  const [selectedText, setSelectedText] = useState('');
  const selectedTextRef = useRef('');

  // Session management
  useEffect(() => {
    const getOrCreateSessionId = () => {
      let sid = localStorage.getItem('chatkit_session_id');
      if (!sid) {
        sid = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
        localStorage.setItem('chatkit_session_id', sid);
      }
      return sid;
    };
    setSessionId(getOrCreateSessionId());
  }, []);

  // Custom fetch with headers
  const customFetch = useCallback(
    async (url, options = {}) => {
      const headers = {
        ...options.headers,
        'X-Session-Id': sessionId,
        'X-Selected-Text': selectedTextRef.current || '',
      };
      return fetch(url, { ...options, headers });
    },
    [sessionId]
  );

  // Initialize ChatKit
  const { control } = useChatKit({
    api: {
      url: 'http://localhost:8001/chatkit',
      domainKey: 'domain_pk_YOUR_KEY_HERE',
      fetch: customFetch,
    },
    startScreen: {
      greeting: 'How can I help you today?',
      prompts: [
        { label: 'Getting started', prompt: 'How do I get started?' },
        { label: 'API reference', prompt: 'Show me the API docs' },
      ],
    },
    composer: {
      placeholder: selectedText
        ? 'Ask about the selected text...'
        : 'Ask me anything...',
    },
    header: { enabled: false },
    history: { enabled: true },
  });

  // Selected text detection
  useEffect(() => {
    const handleTextSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();
      if (text && text.length > 0 && text.length < 2000) {
        setSelectedText(text);
        selectedTextRef.current = text;
      }
    };

    document.addEventListener('mouseup', handleTextSelection);
    return () => document.removeEventListener('mouseup', handleTextSelection);
  }, []);

  return (
    <div style={{ position: 'fixed', bottom: 20, right: 20, zIndex: 9999 }}>
      {control}
    </div>
  );
}
```

2. **Global Integration** (`src/theme/Root.js`):
```javascript
import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import ChatKitBot from '@site/src/components/ChatKitBot';

export default function Root({ children }) {
  return (
    <>
      {children}
      <BrowserOnly>
        {() => <ChatKitBot />}
      </BrowserOnly>
    </>
  );
}
```

3. **Backend Handler** (`backend/chatkit_server.py`):
```python
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai_chatkit import ChatKitServer, StreamingResult
from chatkit_store import CustomChatKitStore
import openai

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
store = CustomChatKitStore()
chatkit_server = ChatKitServer(store=store)
openai_client = openai.AsyncOpenAI()

@chatkit_server.respond()
async def handle_message(context):
    user_text = context["user_message"].content
    selected_text = context.get("metadata", {}).get("selected_text", "")

    # Build prompt with context
    prompt = user_text
    if selected_text:
        prompt = f'Selected text: "{selected_text}"\n\nQuestion: {user_text}'

    # Call your existing AI backend
    response = await openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )

    # Return response
    yield ThreadItemAddedEvent(item=AssistantMessageItem(
        id=str(uuid.uuid4()),
        thread_id=context["thread"].id,
        created_at=datetime.utcnow(),
        content=[AssistantMessageContent(text=response.choices[0].message.content)]
    ))

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    session_id = request.headers.get('X-Session-Id', '')
    selected_text = request.headers.get('X-Selected-Text', '')

    context = {
        "request": request,
        "metadata": {"session_id": session_id, "selected_text": selected_text}
    }

    payload = await request.body()
    result = await chatkit_server.process(payload, context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    else:
        return Response(content=result.json, media_type="application/json")
```

4. **Installation Commands**:
```bash
# Frontend
npm install @openai/chatkit-react

# Backend
cd backend
pip install openai-chatkit fastapi uvicorn sqlalchemy psycopg2-binary

# Run
npm start  # Frontend
python chatkit_server.py  # Backend
```

5. **Setup Instructions** (`CHATKIT_SETUP.md`):
- Get OpenAI domain key from https://platform.openai.com/chatkit
- Configure environment variables
- Set up database (PostgreSQL/SQLite)
- Test locally
- Deploy to production

### Scenario 2: Add ChatKit to Next.js App with Existing RAG Backend

**User Input:**
```
I have a Next.js app with a RAG backend using Qdrant and Cohere. Add ChatKit UI to replace my current chat interface.
```

**What You Get:**

1. **Next.js Component** (`components/ChatKitBot.jsx`):
```javascript
import dynamic from 'next/dynamic';
import { useChatKit } from '@openai/chatkit-react';
// ... (similar to above with Next.js-specific adjustments)
```

2. **App Integration** (`pages/_app.js`):
```javascript
import dynamic from 'next/dynamic';

const ChatKitBot = dynamic(() => import('@/components/ChatKitBot'), {
  ssr: false,
});

function MyApp({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <ChatKitBot />
    </>
  );
}
```

3. **Backend Integration** (connects to your existing RAG):
```python
@chatkit_server.respond()
async def handle_message(context):
    user_text = context["user_message"].content

    # Call your existing RAG system
    embedding = await cohere_client.embed([user_text])
    results = await qdrant_client.search(
        collection_name="your_collection",
        query_vector=embedding[0],
        limit=5
    )

    context_text = "\n\n".join([r.payload["text"] for r in results])

    # Generate response with context
    response = await your_llm.generate(
        f"Context:\n{context_text}\n\nQuestion: {user_text}"
    )

    yield ThreadItemAddedEvent(...)
```

### Scenario 3: Migrate from Existing Chat UI to ChatKit

**User Input:**
```
I have a custom React chat component. Migrate to ChatKit while preserving chat history.
```

**What You Get:**

1. **Migration Script** (`scripts/migrate_chat_history.py`):
```python
from old_chat_db import OldChatDB
from database import ChatSession, ChatMessage, SessionLocal

def migrate_history():
    old_db = OldChatDB()
    new_db = SessionLocal()

    for old_session in old_db.get_all_sessions():
        new_session = ChatSession(
            id=f"migrated_{old_session.id}",
            created_at=old_session.created_at,
        )
        new_db.add(new_session)

        for old_msg in old_db.get_messages(old_session.id):
            new_msg = ChatMessage(
                id=f"migrated_{old_msg.id}",
                session_id=new_session.id,
                role=old_msg.role,
                content=old_msg.content,
                created_at=old_msg.created_at
            )
            new_db.add(new_msg)

    new_db.commit()
```

2. **Side-by-Side Testing Setup**
3. **Feature Parity Checklist**
4. **Gradual Rollout Plan**

## Framework Support Matrix

| Framework | Status | SSR Support | Notes |
|-----------|--------|-------------|-------|
| React (Vite) | ✅ Full | N/A | Direct integration |
| Next.js | ✅ Full | ✅ Yes | Use `dynamic` import |
| Docusaurus | ✅ Full | ✅ Yes | Use `BrowserOnly` |
| Gatsby | ✅ Full | ✅ Yes | Use `gatsby-browser.js` |
| Remix | ✅ Full | ✅ Yes | Use `ClientOnly` |
| Plain HTML | ✅ Full | N/A | CDN script tag |

## Backend Support Matrix

| Backend | Status | Notes |
|---------|--------|-------|
| FastAPI | ✅ Full | Recommended, best streaming support |
| Express.js | ✅ Full | Node.js alternative |
| Django | ✅ Full | Use Django Channels for streaming |
| Flask | ⚠️ Limited | No native streaming support |

## Database Support Matrix

| Database | Status | Notes |
|----------|--------|-------|
| PostgreSQL | ✅ Full | Recommended for production |
| MongoDB | ✅ Full | NoSQL alternative |
| SQLite | ✅ Full | Good for development/small projects |
| MySQL | ✅ Full | Supported via SQLAlchemy |

## AI Backend Support

Works with any AI backend:
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ Anthropic (Claude)
- ✅ Google (Gemini)
- ✅ Local models (Ollama, LM Studio)
- ✅ RAG systems (Qdrant, Pinecone, Weaviate)
- ✅ Custom agents (LangChain, LlamaIndex, etc.)

## Advanced Features Included

### 1. Selected Text Questioning
- Automatically detects text selection
- Shows "Ask about this" button
- Passes selected text to backend as context

### 2. Session Management
- Persistent sessions via localStorage
- Automatic session ID generation
- Session-based chat history

### 3. Streaming Responses
- Real-time response streaming via SSE
- Progressive text display
- Proper error handling

### 4. Database Persistence
- Chat history stored in database
- Session tracking
- Message metadata support

### 5. Custom Styling
- Glass morphism effects
- Dark mode support
- Mobile responsive
- Customizable colors and positioning

### 6. Error Handling
- Network error recovery
- Rate limiting handling
- Graceful degradation
- User-friendly error messages

### 7. Production Features
- CORS configuration
- Rate limiting
- Monitoring and logging
- Health checks
- Metrics collection

## Deployment Support

### Included Deployment Configs

1. **Vercel** (Frontend)
   - `vercel.json`
   - Environment variables setup
   - Build configuration

2. **Render** (Backend)
   - `render.yaml`
   - Database setup
   - Environment variables

3. **Railway** (Full Stack)
   - `railway.json`
   - One-click deployment

4. **Docker**
   - `Dockerfile` (frontend + backend)
   - `docker-compose.yml`
   - Production-ready images

5. **Nginx**
   - Reverse proxy config
   - SSL/TLS setup
   - Streaming support

## Testing Included

### Frontend Tests
- Component rendering
- Session management
- Text selection
- Error handling
- User interactions

### Backend Tests
- Endpoint testing
- Store operations
- Database persistence
- Error scenarios
- Load testing

### Integration Tests
- End-to-end chat flow
- Streaming responses
- Session persistence
- Cross-browser testing

## Troubleshooting Guide Included

Covers all common issues:
- CORS errors
- SSR hydration errors
- Session not persisting
- Streaming not working
- Database connection issues
- Memory leaks
- Performance problems

## Quick Start Commands

After skill execution, you can start immediately:

```bash
# Install dependencies
npm install
cd backend && pip install -r requirements.txt

# Set up environment
cp backend/.env.example backend/.env
# Edit .env with your keys

# Run locally
npm run dev          # Frontend (port 3000)
python backend/chatkit_server.py  # Backend (port 8001)

# Test
npm test             # Frontend tests
pytest backend/      # Backend tests

# Deploy
vercel deploy        # Frontend
# Follow backend deployment guide
```

## Success Criteria

After running this skill, you will have:

- ✅ ChatKit UI integrated into your project
- ✅ Connected to your existing backend
- ✅ Session management working
- ✅ Chat history persisting to database
- ✅ Selected-text questioning (if requested)
- ✅ Streaming responses working
- ✅ Tests passing
- ✅ Production deployment ready
- ✅ Documentation complete
- ✅ Monitoring set up

## Reference Implementation

This skill is based on the production ChatKit integration in:
**PhysicalAI Humanoid Robotics Book Project**
- Live: https://alishbawajahat.github.io/PhysicalAI-humanoid-robotics-book-project/
- Source: `src/components/Chatkit-chatbot/`
- Backend: `backend/chatkit_server.py`

## Expert Agent Reference

For detailed technical documentation, see:
- `.specify/agents/chatkit-expert.md` - Main integration guide
- `.specify/agents/chatkit-expert-supplement.md` - Advanced topics

## Final Output Message

> ✅ **ChatKit Integration Complete!**
>
> Your chatbot UI is ready to deploy. Here's what was created:
>
> **Frontend:**
> - ChatKit component with session management
> - Global integration in your app
> - Custom styling and features
>
> **Backend:**
> - ChatKit endpoint handler
> - Database persistence
> - Connection to your AI backend
>
> **Next Steps:**
> 1. Get your domain key: https://platform.openai.com/chatkit
> 2. Configure `.env` with your keys
> 3. Run `npm install && npm run dev`
> 4. Run `python backend/chatkit_server.py`
> 5. Test at http://localhost:3000
>
> **Deploy:**
> - Frontend: `vercel deploy`
> - Backend: Follow `CHATKIT_DEPLOYMENT.md`
>
> Your users can now chat with your AI through a beautiful, production-ready interface! 🚀

---

**Skill Status:** ✅ Production Ready
**Version:** 1.0.0
**Last Updated:** 2026-02-09
**Compatibility:** React 18+, Python 3.9+, FastAPI 0.100+
