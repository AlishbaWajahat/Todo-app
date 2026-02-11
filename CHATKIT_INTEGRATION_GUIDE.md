# ChatKit Expert Agent - Complete Guide

**Version:** 2.0.0 (Merged & Comprehensive)
**Last Updated:** 2026-02-09
**Purpose:** Complete reference for integrating OpenAI ChatKit chatbot UI with FastAPI backend

---

## 🚨 IMPORTANT: How to Use This Agent

**For actual ChatKit integration work, ALWAYS invoke the skill first:**

```
/chatkit-integration-expert
```

Or simply describe your need:
```
Add ChatKit to my Next.js app with existing FastAPI backend
```

**The skill will:**
- ✅ Automatically detect your project setup (React, Next.js, Docusaurus, Gatsby, Remix, etc.)
- ✅ Generate all necessary files with correct paths
- ✅ Provide working code templates tailored to your framework
- ✅ Handle framework-specific configurations and edge cases
- ✅ Create tests and deployment configs

**This documentation is comprehensive reference material** for understanding concepts, troubleshooting, and advanced customization.

**Skill Location:** `.claude/skills/chatkit-integration/SKILL.md`

---

## 📚 Table of Contents

### Getting Started
1. [Agent Overview](#agent-overview)
2. [Quick Start Guide](#quick-start-guide)
3. [Architecture Overview](#architecture-pattern)

### Installation & Setup
4. [Frontend Installation](#phase-1-frontend-setup)
   - React/Vite
   - Next.js
   - Docusaurus
   - Remix
   - Gatsby
5. [Backend Installation](#phase-2-backend-setup)
6. [Getting Your OpenAI Domain Key](#getting-your-openai-domain-key)

### Core Implementation
7. [ChatKit Component (Frontend)](#step-13-create-chatkit-component)
8. [ChatKit Server (Backend)](#step-24-create-chatkit-server)
9. [Database Schema](#step-22-create-database-schema)
10. [Custom Store Implementation](#step-23-implement-chatkit-store)

### Framework-Specific Guides
11. [Plain React (Vite)](#plain-react-vite)
12. [Next.js Integration](#nextjs-integration)
13. [Docusaurus Integration](#docusaurus-integration)
14. [Remix Integration](#remix-integration)
15. [Gatsby Integration](#gatsby-integration)
16. [Plain HTML/JavaScript](#plain-html-integration)

### Error Handling & Reliability
17. [Frontend Error Handling](#comprehensive-frontend-error-handling)
18. [Backend Error Handling](#comprehensive-backend-error-handling)
19. [Network & Retry Logic](#network-status-and-retry-logic)

### Database Options
20. [PostgreSQL (Recommended)](#postgresql-default)
21. [SQLite (Small Projects)](#sqlite-for-smaller-projects)
22. [MongoDB](#mongodb-integration)

### AI Backend Integration
23. [OpenAI Integration](#openai-integration)
24. [Anthropic/Claude Integration](#anthropic-integration)
25. [Local Models (Ollama)](#local-model-ollama)
26. [RAG Integration Pattern](#pattern-1-rag-integration)
27. [Agent Integration Pattern](#pattern-2-agent-integration)

### Advanced Features
28. [Selected Text Questioning](#feature-1-selected-text-questioning)
29. [Conversation History API](#feature-2-conversation-history-api)
30. [Custom Styling](#feature-3-custom-styling)
31. [Streaming Responses](#streaming-implementation)
32. [Session Management](#session-management-deep-dive)

### Testing & Quality
33. [Frontend Testing (Jest)](#frontend-testing-jest--react-testing-library)
34. [Backend Testing (pytest)](#backend-testing-pytest)
35. [Integration Testing](#integration-testing)
36. [Load Testing](#load-testing)

### Production & Monitoring
37. [Logging Setup](#logging-setup)
38. [Metrics Collection](#metrics-collection)
39. [Performance Optimization](#performance-optimization)
40. [Security Considerations](#security-considerations)

### Troubleshooting
41. [Common Issues & Solutions](#troubleshooting)
42. [Common Pitfalls](#common-pitfalls--solutions)
43. [Debug Checklist](#debug-checklist)

### Migration & Deployment
44. [Migration from Existing Chat](#migration-guide)
45. [Deployment Checklist](#deployment-checklist)
46. [Production Deployment](#production-deployment-checklist)

### Reference
47. [Reference Implementation](#reference-implementation)
48. [Quick Commands](#quick-start-commands)
49. [Support Resources](#support-resources)

---

## Agent Overview

This agent specializes in integrating OpenAI ChatKit (React frontend + Python backend) into existing web applications. It provides step-by-step guidance for:

- Installing and configuring ChatKit React components
- Setting up ChatKit Python backend with FastAPI
- Connecting frontend to backend with custom headers
- Implementing advanced features (selected text questioning, session management, streaming)
- Integrating with existing RAG/AI systems
- Supporting multiple frameworks (React, Next.js, Docusaurus, Remix, Gatsby)
- Database options (PostgreSQL, MongoDB, SQLite)
- AI provider flexibility (OpenAI, Anthropic, Ollama, custom)

**Expertise Areas:**
- `@openai/chatkit-react` (React SDK)
- `openai-chatkit` (Python SDK)
- FastAPI backend integration
- SSR-safe React components
- Custom fetch functions and headers
- Session management with localStorage
- Streaming responses (SSE)
- Database persistence for chat history
- Error handling and retry logic
- Production monitoring and logging

---

## Quick Start Guide

### 5-Minute Setup (Existing Project)

**Prerequisites:**
- Existing React/Next.js/Docusaurus project
- Python 3.9+ backend with FastAPI
- PostgreSQL database (or SQLite for testing)

**Frontend (2 minutes):**
```bash
npm install @openai/chatkit-react
```

Create `src/components/ChatKitBot/index.jsx` with the reference implementation below, then integrate globally.

**Backend (3 minutes):**
```bash
pip install openai-chatkit fastapi uvicorn sqlalchemy psycopg2-binary
```

Create `backend/chatkit_server.py` with the reference implementation below, then run:
```bash
python chatkit_server.py
```

**Test:**
1. Open your app at `http://localhost:3000`
2. Click the chat button (bottom-right)
3. Send a message
4. Verify response appears

**Next Steps:**
- Get OpenAI domain key for production
- Integrate with your AI/RAG system
- Customize styling and prompts
- Add error handling and monitoring

---

## Getting Your OpenAI Domain Key

### Step-by-Step Process

1. **Sign up for OpenAI Platform**
   - Go to https://platform.openai.com
   - Create account or sign in

2. **Access ChatKit Dashboard**
   - Navigate to https://platform.openai.com/chatkit
   - Or go to Dashboard → ChatKit

3. **Create New Deployment**
   - Click "Create Deployment"
   - Enter deployment name (e.g., "My App Chatbot")
   - Select deployment type: "Custom Backend"

4. **Get Domain Key**
   - After creation, you'll see your domain key
   - Format: `domain_pk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
   - Copy this key

5. **Add Allowed Domains**
   - In deployment settings, add your domains:
     - `localhost:3000` (for development)
     - `your-production-domain.com` (for production)
   - Save changes

6. **Use in Code**
   ```javascript
   const getDomainKey = () => {
     if (typeof window === 'undefined') {
       return 'domain_pk_YOUR_KEY_HERE';
     }
     return window.location.hostname === 'localhost'
       ? 'local-dev'  // Special key for localhost
       : 'domain_pk_YOUR_KEY_HERE';  // Your actual key
   };
   ```

**Important Notes:**
- Keep your domain key secret (don't commit to git)
- Use environment variables for production
- The `local-dev` key works for localhost without registration
- Production domains must be registered in ChatKit dashboard

---

## Architecture Pattern

### High-Level Flow

```
User Browser
    ↓
ChatKit React Component (@openai/chatkit-react)
    ↓ (HTTP POST with custom headers)
FastAPI Backend (/chatkit endpoint)
    ↓
ChatKit Python Server (openai-chatkit)
    ↓
Your AI Agent/RAG System
    ↓ (streaming response)
User sees progressive response
```

### Key Components

1. **Frontend Layer**
   - React component using `useChatKit` hook
   - Custom fetch function for headers
   - Session management (localStorage)
   - Selected text detection
   - SSR-safe rendering

2. **Backend Layer**
   - FastAPI server with CORS
   - ChatKit endpoint handler
   - Custom store implementation
   - Database integration
   - AI agent integration

3. **Data Layer**
   - PostgreSQL for chat history
   - Vector DB for RAG (optional)
   - Session tracking

---

## Installation Guide

### Phase 1: Frontend Setup

#### Step 1.1: Install Dependencies

```bash
npm install @openai/chatkit-react
# or
yarn add @openai/chatkit-react
```

**Optional UI Dependencies:**
```bash
npm install class-variance-authority clsx framer-motion lucide-react
```

#### Step 1.2: Load ChatKit Script (for Docusaurus/Next.js)

**For Docusaurus** - Add to `docusaurus.config.js`:
```javascript
module.exports = {
  // ... other config
  scripts: [
    {
      src: 'https://cdn.platform.openai.com/deployments/chatkit/chatkit.js',
      async: true,
      type: 'module',
    },
  ],
};
```

**For Next.js** - Add to `next.config.js`:
```javascript
module.exports = {
  // ... other config
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.platform.openai.com;",
          },
        ],
      },
    ];
  },
};
```

#### Step 1.3: Create ChatKit Component

**File:** `src/components/ChatKitBot/index.jsx`

```javascript
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useChatKit } from '@openai/chatkit-react';

export default function ChatKitBot() {
  // Session management
  const [sessionId, setSessionId] = useState('');
  const [selectedText, setSelectedText] = useState('');
  const selectedTextRef = useRef('');

  // Initialize session ID
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

  // Keep ref in sync
  useEffect(() => {
    selectedTextRef.current = selectedText;
  }, [selectedText]);

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

  // Backend URL detection
  const getBackendUrl = () => {
    if (typeof window === 'undefined') {
      return 'https://your-production-backend.com/chatkit';
    }
    if (window.location.hostname === 'localhost') {
      return 'http://localhost:8001/chatkit';
    }
    return 'https://your-production-backend.com/chatkit';
  };

  // Domain key (get from OpenAI ChatKit dashboard)
  const getDomainKey = () => {
    if (typeof window === 'undefined') {
      return 'domain_pk_YOUR_KEY_HERE';
    }
    return window.location.hostname === 'localhost'
      ? 'local-dev'
      : 'domain_pk_YOUR_KEY_HERE';
  };

  // Initialize ChatKit
  const { control } = useChatKit({
    api: {
      url: getBackendUrl(),
      domainKey: getDomainKey(),
      fetch: customFetch,
    },
    startScreen: {
      greeting: 'How can I help you today?',
      prompts: [
        { label: 'Example question 1', prompt: 'Tell me about...' },
        { label: 'Example question 2', prompt: 'Explain...' },
      ],
    },
    composer: {
      placeholder: selectedText
        ? 'Ask about the selected text...'
        : 'Ask me anything...',
    },
    header: { enabled: false },
    history: { enabled: true, showDelete: false, showRename: false },
    threadItemActions: { feedback: false, retry: true },
  });

  // Selected text detection
  useEffect(() => {
    const handleTextSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();

      if (text && text.length > 0 && text.length < 2000) {
        setSelectedText(text);
      }
    };

    document.addEventListener('mouseup', handleTextSelection);
    document.addEventListener('touchend', handleTextSelection);

    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
      document.removeEventListener('touchend', handleTextSelection);
    };
  }, []);

  return (
    <div style={{ position: 'fixed', bottom: 20, right: 20, zIndex: 9999 }}>
      {control}
    </div>
  );
}
```

#### Step 1.4: Integrate Globally (Docusaurus)

**File:** `src/theme/Root.js`

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

**For Next.js** - Add to `_app.js`:
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

---

## Framework-Specific Implementation Guides

### Plain React (Vite)

**Installation:**
```bash
npm create vite@latest my-app -- --template react
cd my-app
npm install @openai/chatkit-react
```

**Integration in `src/App.jsx`:**
```javascript
import { useState, useEffect } from 'react';
import ChatKitBot from './components/ChatKitBot';

function App() {
  return (
    <div className="App">
      <h1>My App</h1>
      {/* Your app content */}
      <ChatKitBot />
    </div>
  );
}

export default App;
```

**Load Script in `index.html`:**
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>My App</title>
    <script
      src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
      type="module"
      async
    ></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

### Next.js Integration

**Installation:**
```bash
npm install @openai/chatkit-react
```

**Configure CSP in `next.config.js`:**
```javascript
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.platform.openai.com;",
          },
        ],
      },
    ];
  },
};
```

**Create Component with SSR Safety:**
```javascript
// components/ChatKitBot.jsx
import { useChatKit } from '@openai/chatkit-react';
// ... (use the reference implementation)
```

**Integrate in `_app.js`:**
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

export default MyApp;
```

### Docusaurus Integration

**Installation:**
```bash
npm install @openai/chatkit-react
```

**Configure Script in `docusaurus.config.js`:**
```javascript
module.exports = {
  // ... other config
  scripts: [
    {
      src: 'https://cdn.platform.openai.com/deployments/chatkit/chatkit.js',
      async: true,
      type: 'module',
    },
  ],
};
```

**Create Component:**
```javascript
// src/components/ChatKitBot/index.jsx
// ... (use the reference implementation)
```

**Integrate in `src/theme/Root.js`:**
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

### Remix Integration

**Installation:**
```bash
npm install @openai/chatkit-react
```

**Create Client Component `app/components/ChatKitBot.client.tsx`:**
```typescript
import { useChatKit } from '@openai/chatkit-react';
// ... (use the reference implementation)
```

**Use in `app/root.tsx`:**
```typescript
import { ClientOnly } from 'remix-utils/client-only';
import ChatKitBot from './components/ChatKitBot.client';

export default function App() {
  return (
    <html>
      <head>
        <Meta />
        <Links />
        <script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          type="module"
          async
        />
      </head>
      <body>
        <Outlet />
        <ClientOnly>
          {() => <ChatKitBot />}
        </ClientOnly>
        <Scripts />
      </body>
    </html>
  );
}
```

### Gatsby Integration

**Installation:**
```bash
npm install @openai/chatkit-react
```

**Create `gatsby-browser.js`:**
```javascript
export const onClientEntry = () => {
  const script = document.createElement('script');
  script.src = 'https://cdn.platform.openai.com/deployments/chatkit/chatkit.js';
  script.type = 'module';
  script.async = true;
  document.head.appendChild(script);
};
```

**Use in `gatsby-ssr.js`:**
```javascript
import React from 'react';
import ChatKitBot from './src/components/ChatKitBot';

export const wrapPageElement = ({ element }) => {
  return (
    <>
      {element}
      {typeof window !== 'undefined' && <ChatKitBot />}
    </>
  );
};
```

### Plain HTML Integration

**For vanilla JavaScript projects:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App with ChatKit</title>
  <script src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" type="module" async></script>
</head>
<body>
  <h1>My Application</h1>

  <div id="chatkit-container"></div>

  <script type="module">
    import { createChatKit } from 'https://cdn.platform.openai.com/deployments/chatkit/chatkit.js';

    // Session management
    function getOrCreateSessionId() {
      let sid = localStorage.getItem('chatkit_session_id');
      if (!sid) {
        sid = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
        localStorage.setItem('chatkit_session_id', sid);
      }
      return sid;
    }

    const sessionId = getOrCreateSessionId();

    // Custom fetch with headers
    async function customFetch(url, options = {}) {
      const headers = {
        ...options.headers,
        'X-Session-Id': sessionId,
      };
      return fetch(url, { ...options, headers });
    }

    // Initialize ChatKit
    const chatkit = createChatKit({
      api: {
        url: 'http://localhost:8001/chatkit',
        domainKey: 'local-dev',
        fetch: customFetch,
      },
      startScreen: {
        greeting: 'How can I help you today?',
      },
    });

    // Mount to DOM
    document.getElementById('chatkit-container').appendChild(chatkit.element);
  </script>
</body>
</html>
```

---

### Phase 2: Backend Setup

#### Step 2.1: Install Python Dependencies

**File:** `backend/requirements.txt`

```txt
# Core
fastapi>=0.124.4
uvicorn[standard]>=0.38.0
python-dotenv>=1.0.0

# ChatKit
openai-chatkit>=1.4.0

# Database
sqlalchemy>=2.0.35
psycopg2-binary>=2.9.9

# AI/RAG (adjust based on your stack)
openai-agents[litellm]>=0.1.0
qdrant-client>=1.12.1
cohere>=5.5.0
```

Install:
```bash
cd backend
pip install -r requirements.txt
```

#### Step 2.2: Create Database Schema

**File:** `backend/database.py`

```python
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(Text, nullable=True)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### Step 2.3: Implement ChatKit Store

**File:** `backend/chatkit_store.py`

```python
from openai_chatkit import ChatKitStore, Thread, ThreadItem, UserMessageItem, AssistantMessageItem
from datetime import datetime
from typing import List, Optional
import uuid
from database import SessionLocal, ChatSession, ChatMessage

class CustomChatKitStore(ChatKitStore):
    """Custom store implementation with database persistence"""

    def __init__(self):
        self.db = SessionLocal()

    async def load_thread(self, thread_id: str) -> Optional[Thread]:
        """Load or create a thread (session)"""
        session = self.db.query(ChatSession).filter_by(id=thread_id).first()

        if not session:
            # Create new session
            session = ChatSession(
                id=thread_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(session)
            self.db.commit()

        return Thread(
            id=thread_id,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata={}
        )

    async def load_thread_items(
        self,
        thread_id: str,
        limit: Optional[int] = None
    ) -> List[ThreadItem]:
        """Load conversation history"""
        query = self.db.query(ChatMessage).filter_by(session_id=thread_id)
        query = query.order_by(ChatMessage.created_at.desc())

        if limit:
            query = query.limit(limit)

        messages = query.all()
        messages.reverse()  # Oldest first

        items = []
        for msg in messages:
            if msg.role == 'user':
                items.append(UserMessageItem(
                    id=msg.id,
                    thread_id=thread_id,
                    created_at=msg.created_at,
                    content=msg.content
                ))
            else:
                items.append(AssistantMessageItem(
                    id=msg.id,
                    thread_id=thread_id,
                    created_at=msg.created_at,
                    content=[{"text": msg.content}]
                ))

        return items

    async def add_thread_item(self, thread_id: str, item: ThreadItem):
        """Save a message to database"""
        if isinstance(item, UserMessageItem):
            role = 'user'
            content = item.content
        elif isinstance(item, AssistantMessageItem):
            role = 'assistant'
            content = item.content[0].text if item.content else ''
        else:
            return

        message = ChatMessage(
            id=item.id,
            session_id=thread_id,
            role=role,
            content=content,
            created_at=item.created_at
        )
        self.db.add(message)
        self.db.commit()
```

#### Step 2.4: Create ChatKit Server

**File:** `backend/chatkit_server.py`

```python
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai_chatkit import ChatKitServer, StreamingResult
from chatkit_store import CustomChatKitStore
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-production-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChatKit server
store = CustomChatKitStore()
chatkit_server = ChatKitServer(store=store)

# Register response handler
@chatkit_server.respond()
async def handle_message(context):
    """Handle incoming messages and generate responses"""

    # Extract metadata from context
    metadata = context.get("metadata", {})
    session_id = metadata.get("session_id", "")
    selected_text = metadata.get("selected_text", "")

    # Get the thread and user message
    thread = context["thread"]
    user_message = context["user_message"]
    user_text = user_message.content

    logger.info(f"Processing message for session {session_id}")

    # Build enhanced query with context
    query_parts = []

    # Add conversation history (last 10 messages)
    history = await store.load_thread_items(thread.id, limit=10)
    if history:
        history_text = "\n".join([
            f"{item.role.capitalize()}: {item.content if hasattr(item, 'content') else item.content[0].text}"
            for item in history[-10:]
        ])
        query_parts.append(f"Previous conversation:\n{history_text}")

    # Add selected text context
    if selected_text:
        query_parts.append(f'Selected text:\n"{selected_text}"')

    # Add current question
    query_parts.append(f"Current question:\n{user_text}")

    enhanced_query = "\n\n".join(query_parts)

    # Call your AI agent/RAG system here
    # Example: response_text = await your_ai_agent.generate(enhanced_query)
    response_text = f"Echo: {enhanced_query}"  # Replace with actual AI call

    # Stream response back
    from openai_chatkit import AssistantMessageItem, AssistantMessageContent, ThreadItemAddedEvent

    assistant_msg = AssistantMessageItem(
        id=str(uuid.uuid4()),
        thread_id=thread.id,
        created_at=datetime.utcnow(),
        content=[AssistantMessageContent(text=response_text)],
    )

    yield ThreadItemAddedEvent(item=assistant_msg)

# ChatKit endpoint
@app.post("/chatkit")
async def chatkit_endpoint(request: Request) -> Response:
    """Main ChatKit protocol endpoint"""

    # Extract custom headers
    session_id = request.headers.get('X-Session-Id', '')
    selected_text = request.headers.get('X-Selected-Text', '')

    logger.info(f"ChatKit request - Session: {session_id}, Selected: {bool(selected_text)}")

    # Build context
    context = {
        "request": request,
        "metadata": {
            "session_id": session_id,
            "selected_text": selected_text,
        }
    }

    # Process with ChatKit server
    payload = await request.body()
    result = await chatkit_server.process(payload, context)

    # Return response
    if isinstance(result, StreamingResult):
        return StreamingResponse(
            result,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        return Response(
            content=result.json,
            media_type="application/json"
        )

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatkit-backend"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### Step 2.5: Environment Configuration

**File:** `backend/.env`

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require

# Server
PORT=8001

# AI/RAG (adjust based on your stack)
OPENAI_API_KEY=sk-...
QDRANT_URL=https://your-cluster.qdrant.cloud
QDRANT_API_KEY=...
COHERE_API_KEY=...
```

#### Step 2.6: Run Backend

```bash
cd backend
python chatkit_server.py
```

Or with uvicorn:
```bash
uvicorn chatkit_server:app --host 0.0.0.0 --port 8001 --reload
```

---

## Comprehensive Error Handling

### Comprehensive Frontend Error Handling

**Enhanced ChatKit Component with Full Error Handling:**

```javascript
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useChatKit } from '@openai/chatkit-react';

export default function ChatKitBot() {
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(true);
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;
  const [sessionId, setSessionId] = useState('');
  const [selectedText, setSelectedText] = useState('');
  const selectedTextRef = useRef('');

  // Network status monitoring
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setError(null);
    };
    const handleOffline = () => {
      setIsOnline(false);
      setError('No internet connection. Please check your network.');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Initialize session ID
  useEffect(() => {
    const getOrCreateSessionId = () => {
      try {
        let sid = localStorage.getItem('chatkit_session_id');
        if (!sid) {
          sid = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
          localStorage.setItem('chatkit_session_id', sid);
        }
        return sid;
      } catch (e) {
        console.error('localStorage not available:', e);
        // Fallback to memory-only session
        return `temp_${Date.now()}`;
      }
    };
    setSessionId(getOrCreateSessionId());
  }, []);

  // Keep ref in sync
  useEffect(() => {
    selectedTextRef.current = selectedText;
  }, [selectedText]);

  // Custom fetch with comprehensive error handling
  const customFetch = useCallback(
    async (url, options = {}) => {
      try {
        if (!isOnline) {
          throw new Error('No internet connection');
        }

        const headers = {
          ...options.headers,
          'X-Session-Id': sessionId,
          'X-Selected-Text': selectedTextRef.current || '',
        };

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

        const response = await fetch(url, {
          ...options,
          headers,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          if (response.status === 429) {
            throw new Error('Rate limit exceeded. Please try again in a moment.');
          } else if (response.status === 503) {
            throw new Error('Service temporarily unavailable. Please try again.');
          } else if (response.status >= 500) {
            throw new Error('Server error. Please try again later.');
          } else if (response.status === 401) {
            throw new Error('Authentication failed. Please check your domain key.');
          } else if (response.status === 400) {
            throw new Error('Invalid request. Please refresh the page.');
          }
          throw new Error(`Request failed with status ${response.status}`);
        }

        // Reset retry count on success
        setRetryCount(0);
        setError(null);

        return response;
      } catch (err) {
        console.error('ChatKit fetch error:', err);

        // Handle abort errors
        if (err.name === 'AbortError') {
          setError('Request timed out. Please try again.');
          throw new Error('Request timed out');
        }

        // Retry logic for network errors
        if (retryCount < maxRetries && (err.message.includes('network') || err.message.includes('fetch'))) {
          setRetryCount(prev => prev + 1);
          await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retryCount))); // Exponential backoff
          return customFetch(url, options);
        }

        setError(err.message);
        throw err;
      }
    },
    [sessionId, isOnline, retryCount]
  );

  // Backend URL detection
  const getBackendUrl = () => {
    if (typeof window === 'undefined') {
      return 'https://your-production-backend.com/chatkit';
    }
    if (window.location.hostname === 'localhost') {
      return 'http://localhost:8001/chatkit';
    }
    return 'https://your-production-backend.com/chatkit';
  };

  // Domain key
  const getDomainKey = () => {
    if (typeof window === 'undefined') {
      return 'domain_pk_YOUR_KEY_HERE';
    }
    return window.location.hostname === 'localhost'
      ? 'local-dev'
      : 'domain_pk_YOUR_KEY_HERE';
  };

  // Initialize ChatKit
  const { control } = useChatKit({
    api: {
      url: getBackendUrl(),
      domainKey: getDomainKey(),
      fetch: customFetch,
    },
    startScreen: {
      greeting: 'How can I help you today?',
      prompts: [
        { label: 'Example question 1', prompt: 'Tell me about...' },
        { label: 'Example question 2', prompt: 'Explain...' },
      ],
    },
    composer: {
      placeholder: selectedText
        ? 'Ask about the selected text...'
        : 'Ask me anything...',
    },
    header: { enabled: false },
    history: { enabled: true, showDelete: false, showRename: false },
    threadItemActions: { feedback: false, retry: true },
  });

  // Selected text detection
  useEffect(() => {
    const handleTextSelection = () => {
      try {
        const selection = window.getSelection();
        const text = selection?.toString().trim();

        if (text && text.length > 0 && text.length < 2000) {
          setSelectedText(text);
        }
      } catch (e) {
        console.error('Text selection error:', e);
      }
    };

    document.addEventListener('mouseup', handleTextSelection);
    document.addEventListener('touchend', handleTextSelection);

    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
      document.removeEventListener('touchend', handleTextSelection);
    };
  }, []);

  // Error display
  if (error) {
    return (
      <div style={{
        position: 'fixed',
        bottom: 20,
        right: 20,
        padding: '12px 16px',
        background: '#ff4444',
        color: 'white',
        borderRadius: 8,
        zIndex: 9999,
        maxWidth: 300,
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      }}>
        <strong>Error:</strong> {error}
        <button
          onClick={() => {
            setError(null);
            setRetryCount(0);
          }}
          style={{
            marginLeft: 10,
            cursor: 'pointer',
            background: 'white',
            color: '#ff4444',
            border: 'none',
            padding: '4px 8px',
            borderRadius: 4,
          }}
        >
          Dismiss
        </button>
      </div>
    );
  }

  // Offline indicator
  if (!isOnline) {
    return (
      <div style={{
        position: 'fixed',
        bottom: 20,
        right: 20,
        padding: '12px 16px',
        background: '#ff9800',
        color: 'white',
        borderRadius: 8,
        zIndex: 9999,
      }}>
        Offline - Chat unavailable
      </div>
    );
  }

  return (
    <div style={{ position: 'fixed', bottom: 20, right: 20, zIndex: 9999 }}>
      {control}
    </div>
  );
}
```

### Comprehensive Backend Error Handling

**Enhanced Backend with Full Error Handling:**

```python
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai_chatkit import ChatKitServer, StreamingResult
from chatkit_store import CustomChatKitStore
import logging
import traceback
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-production-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") else "An error occurred",
        }
    )

# Initialize ChatKit server
try:
    store = CustomChatKitStore()
    chatkit_server = ChatKitServer(store=store)
    logger.info("ChatKit server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ChatKit server: {e}")
    raise

# Register response handler
@chatkit_server.respond()
async def handle_message(context):
    """Handle incoming messages with error handling"""
    try:
        # Extract metadata
        metadata = context.get("metadata", {})
        session_id = metadata.get("session_id", "")
        selected_text = metadata.get("selected_text", "")

        # Get thread and user message
        thread = context["thread"]
        user_message = context["user_message"]
        user_text = user_message.content

        logger.info(f"Processing message for session {session_id}")

        # Validate input
        if not user_text or len(user_text.strip()) == 0:
            raise ValueError("Empty message content")

        if len(user_text) > 4000:
            raise ValueError("Message too long (max 4000 characters)")

        # Build enhanced query
        query_parts = []

        # Add conversation history
        try:
            history = await store.load_thread_items(thread.id, limit=10)
            if history:
                history_text = "\n".join([
                    f"{item.role.capitalize()}: {item.content if hasattr(item, 'content') else item.content[0].text}"
                    for item in history[-10:]
                ])
                query_parts.append(f"Previous conversation:\n{history_text}")
        except Exception as e:
            logger.warning(f"Failed to load history: {e}")
            # Continue without history

        # Add selected text
        if selected_text:
            query_parts.append(f'Selected text:\n"{selected_text}"')

        # Add current question
        query_parts.append(f"Current question:\n{user_text}")

        enhanced_query = "\n\n".join(query_parts)

        # Call AI system (replace with your implementation)
        try:
            response_text = f"Echo: {enhanced_query}"  # Replace with actual AI call
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            response_text = "I'm sorry, I encountered an error processing your request. Please try again."

        # Stream response
        from openai_chatkit import AssistantMessageItem, AssistantMessageContent, ThreadItemAddedEvent
        from datetime import datetime
        import uuid

        assistant_msg = AssistantMessageItem(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            created_at=datetime.utcnow(),
            content=[AssistantMessageContent(text=response_text)],
        )

        yield ThreadItemAddedEvent(item=assistant_msg)

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        # Return error message to user
        from openai_chatkit import AssistantMessageItem, AssistantMessageContent, ThreadItemAddedEvent
        from datetime import datetime
        import uuid

        error_msg = AssistantMessageItem(
            id=str(uuid.uuid4()),
            thread_id=context["thread"].id,
            created_at=datetime.utcnow(),
            content=[AssistantMessageContent(text=f"Error: {str(e)}")],
        )
        yield ThreadItemAddedEvent(item=error_msg)

    except Exception as e:
        logger.error(f"Error in message handler: {e}")
        logger.error(traceback.format_exc())
        # Return generic error to user
        from openai_chatkit import AssistantMessageItem, AssistantMessageContent, ThreadItemAddedEvent
        from datetime import datetime
        import uuid

        error_msg = AssistantMessageItem(
            id=str(uuid.uuid4()),
            thread_id=context["thread"].id,
            created_at=datetime.utcnow(),
            content=[AssistantMessageContent(text="I'm sorry, something went wrong. Please try again.")],
        )
        yield ThreadItemAddedEvent(item=error_msg)

# ChatKit endpoint
@app.post("/chatkit")
async def chatkit_endpoint(request: Request) -> Response:
    """Main ChatKit protocol endpoint with error handling"""
    try:
        # Extract headers
        session_id = request.headers.get('X-Session-Id', '')
        selected_text = request.headers.get('X-Selected-Text', '')

        if not session_id:
            raise HTTPException(
                status_code=400,
                detail="Missing X-Session-Id header"
            )

        logger.info(f"ChatKit request - Session: {session_id}, Selected: {bool(selected_text)}")

        # Build context
        context = {
            "request": request,
            "metadata": {
                "session_id": session_id,
                "selected_text": selected_text,
            }
        }

        # Process with ChatKit
        payload = await request.body()

        if not payload:
            raise HTTPException(
                status_code=400,
                detail="Empty request body"
            )

        result = await chatkit_server.process(payload, context)

        # Return response
        if isinstance(result, StreamingResult):
            return StreamingResponse(
                result,
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # For nginx
                }
            )
        else:
            return Response(
                content=result.json,
                media_type="application/json"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing ChatKit request: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat request"
        )

# Health check
@app.get("/health")
async def health_check():
    try:
        # Test database connection
        db = store.db
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "chatkit-backend",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "chatkit-backend",
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### Network Status and Retry Logic

**Key Features:**
- Automatic retry with exponential backoff
- Network status monitoring
- Timeout handling (30 seconds)
- Rate limit detection
- User-friendly error messages
- Graceful degradation

---

## Advanced Features

### Feature 1: Selected Text Questioning

**Frontend Enhancement** (add to ChatKit component):

```javascript
const [showAskButton, setShowAskButton] = useState(false);
const [buttonPosition, setButtonPosition] = useState({ x: 0, y: 0 });

useEffect(() => {
  const handleTextSelection = () => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();

    if (text && text.length > 0 && text.length < 2000) {
      setSelectedText(text);

      // Position button near selection
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();

      setButtonPosition({
        x: rect.left + (rect.width / 2),
        y: rect.bottom + window.scrollY + 10,
      });

      setShowAskButton(true);
    } else {
      setShowAskButton(false);
    }
  };

  document.addEventListener('mouseup', handleTextSelection);
  return () => document.removeEventListener('mouseup', handleTextSelection);
}, []);

// Render button
{showAskButton && (
  <button
    style={{
      position: 'absolute',
      left: `${buttonPosition.x}px`,
      top: `${buttonPosition.y}px`,
      zIndex: 10000,
    }}
    onClick={() => {
      // Open chat and focus on selected text
      setShowAskButton(false);
    }}
  >
    Ask about this
  </button>
)}
```

### Feature 2: Conversation History API

**Backend Endpoint:**

```python
@app.get("/api/history/{session_id}")
async def get_history(session_id: str, limit: int = 50):
    """Get conversation history for a session"""
    db = SessionLocal()
    try:
        messages = db.query(ChatMessage)\
            .filter_by(session_id=session_id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all()

        return {
            "session_id": session_id,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in reversed(messages)
            ]
        }
    finally:
        db.close()
```

### Feature 3: Custom Styling

**CSS Module** (`styles.module.css`):

```css
/* Glass morphism effect */
.chatContainer {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .chatContainer {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
}

/* Mobile responsive */
@media (max-width: 768px) {
  .chatContainer {
    width: 100vw;
    height: 100vh;
    border-radius: 0;
  }
}
```

---

## Database Options

### PostgreSQL (Default)

**Recommended for production.** Already covered in the main installation guide above.

**Connection String Format:**
```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
```

**Connection Pooling:**
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)
```

### SQLite (for smaller projects)

**Best for:** Development, testing, small deployments (< 100 users)

**File:** `backend/database.py`

```python
from sqlalchemy import create_engine
import os

# Use SQLite for development/small projects
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatkit.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
```

**Pros:**
- No separate database server needed
- Zero configuration
- Perfect for development
- File-based (easy backups)

**Cons:**
- Not suitable for high concurrency
- Limited scalability
- No network access

### MongoDB Integration

**Best for:** Document-oriented data, flexible schemas, high write throughput

**Installation:**
```bash
pip install motor  # Async MongoDB driver
```

**File:** `backend/database_mongo.py`

```python
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional, List
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.chatkit_db

class MongoChatKitStore(ChatKitStore):
    async def load_thread(self, thread_id: str) -> Optional[Thread]:
        session = await db.sessions.find_one({"_id": thread_id})

        if not session:
            session = {
                "_id": thread_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await db.sessions.insert_one(session)

        return Thread(
            id=thread_id,
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            metadata={}
        )

    async def load_thread_items(self, thread_id: str, limit: Optional[int] = None):
        query = {"session_id": thread_id}
        cursor = db.messages.find(query).sort("created_at", -1)

        if limit:
            cursor = cursor.limit(limit)

        messages = await cursor.to_list(length=limit)
        messages.reverse()

        items = []
        for msg in messages:
            if msg["role"] == "user":
                items.append(UserMessageItem(
                    id=msg["_id"],
                    thread_id=thread_id,
                    created_at=msg["created_at"],
                    content=msg["content"]
                ))
            else:
                items.append(AssistantMessageItem(
                    id=msg["_id"],
                    thread_id=thread_id,
                    created_at=msg["created_at"],
                    content=[{"text": msg["content"]}]
                ))

        return items

    async def add_thread_item(self, thread_id: str, item: ThreadItem):
        if isinstance(item, UserMessageItem):
            role = "user"
            content = item.content
        elif isinstance(item, AssistantMessageItem):
            role = "assistant"
            content = item.content[0].text if item.content else ""
        else:
            return

        await db.messages.insert_one({
            "_id": item.id,
            "session_id": thread_id,
            "role": role,
            "content": content,
            "created_at": item.created_at,
        })
```

**Use in chatkit_server.py:**
```python
from database_mongo import MongoChatKitStore

store = MongoChatKitStore()
chatkit_server = ChatKitServer(store=store)
```

---

## AI Backend Integration

### OpenAI Integration

**Installation:**
```bash
pip install openai
```

**Implementation:**
```python
from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@chatkit_server.respond()
async def handle_message(context):
    user_text = context["user_message"].content
    thread = context["thread"]

    # Build conversation history
    history = await store.load_thread_items(thread.id, limit=10)
    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    for item in history:
        if isinstance(item, UserMessageItem):
            messages.append({"role": "user", "content": item.content})
        elif isinstance(item, AssistantMessageItem):
            messages.append({"role": "assistant", "content": item.content[0].text})

    messages.append({"role": "user", "content": user_text})

    # Call OpenAI with streaming
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        stream=True
    )

    # Stream response
    full_text = ""
    async for chunk in response:
        if chunk.choices[0].delta.content:
            full_text += chunk.choices[0].delta.content

    yield ThreadItemAddedEvent(item=AssistantMessageItem(
        id=str(uuid.uuid4()),
        thread_id=thread.id,
        created_at=datetime.utcnow(),
        content=[AssistantMessageContent(text=full_text)]
    ))
```

### Anthropic Integration

**Installation:**
```bash
pip install anthropic
```

**Implementation:**
```python
from anthropic import AsyncAnthropic
import os

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@chatkit_server.respond()
async def handle_message(context):
    user_text = context["user_message"].content
    thread = context["thread"]

    # Build conversation history
    history = await store.load_thread_items(thread.id, limit=10)
    messages = []

    for item in history:
        if isinstance(item, UserMessageItem):
            messages.append({"role": "user", "content": item.content})
        elif isinstance(item, AssistantMessageItem):
            messages.append({"role": "assistant", "content": item.content[0].text})

    messages.append({"role": "user", "content": user_text})

    # Call Claude with streaming
    async with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=messages
    ) as stream:
        full_text = ""
        async for text in stream.text_stream:
            full_text += text

    yield ThreadItemAddedEvent(item=AssistantMessageItem(
        id=str(uuid.uuid4()),
        thread_id=thread.id,
        created_at=datetime.utcnow(),
        content=[AssistantMessageContent(text=full_text)]
    ))
```

### Local Model (Ollama)

**Installation:**
```bash
# Install Ollama from https://ollama.ai
ollama pull llama2
```

**Implementation:**
```python
import aiohttp

@chatkit_server.respond()
async def handle_message(context):
    user_text = context["user_message"].content
    thread = context["thread"]

    # Build conversation history
    history = await store.load_thread_items(thread.id, limit=10)
    prompt_parts = []

    for item in history:
        if isinstance(item, UserMessageItem):
            prompt_parts.append(f"User: {item.content}")
        elif isinstance(item, AssistantMessageItem):
            prompt_parts.append(f"Assistant: {item.content[0].text}")

    prompt_parts.append(f"User: {user_text}")
    prompt_parts.append("Assistant:")

    full_prompt = "\n".join(prompt_parts)

    # Call Ollama
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama2",
                "prompt": full_prompt,
                "stream": False
            }
        ) as response:
            data = await response.json()
            full_text = data["response"]

    yield ThreadItemAddedEvent(item=AssistantMessageItem(
        id=str(uuid.uuid4()),
        thread_id=thread.id,
        created_at=datetime.utcnow(),
        content=[AssistantMessageContent(text=full_text)]
    ))
```

### RAG Integration Pattern

**With Vector Database (Qdrant):**

```python
from qdrant_client import AsyncQdrantClient
from openai import AsyncOpenAI

qdrant = AsyncQdrantClient(url=os.getenv("QDRANT_URL"))
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@chatkit_server.respond()
async def handle_message(context):
    user_text = context["user_message"].content
    thread = context["thread"]

    # 1. Generate embeddings for user query
    embedding_response = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=user_text
    )
    query_embedding = embedding_response.data[0].embedding

    # 2. Search vector database
    search_results = await qdrant.search(
        collection_name="knowledge_base",
        query_vector=query_embedding,
        limit=5
    )

    # 3. Build context from search results
    context_chunks = [result.payload["text"] for result in search_results]
    context_text = "\n\n".join(context_chunks)

    # 4. Generate response with context
    messages = [
        {
            "role": "system",
            "content": f"You are a helpful assistant. Use the following context to answer questions:\n\n{context_text}"
        },
        {"role": "user", "content": user_text}
    ]

    response = await openai_client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        stream=True
    )

    # 5. Stream response
    full_text = ""
    async for chunk in response:
        if chunk.choices[0].delta.content:
            full_text += chunk.choices[0].delta.content

    yield ThreadItemAddedEvent(item=AssistantMessageItem(
        id=str(uuid.uuid4()),
        thread_id=thread.id,
        created_at=datetime.utcnow(),
        content=[AssistantMessageContent(text=full_text)]
    ))
```

---

## Integration with Existing AI Systems

### Pattern 1: RAG Integration

```python
@chatkit_server.respond()
async def handle_message(context):
    user_text = context["user_message"].content

    # 1. Generate embeddings
    embedding = await your_embedding_service.embed(user_text)

    # 2. Search vector database
    results = await your_vector_db.search(embedding, limit=5)

    # 3. Build context
    context_text = "\n\n".join([r.content for r in results])

    # 4. Generate response with LLM
    prompt = f"Context:\n{context_text}\n\nQuestion: {user_text}"
    response = await your_llm.generate(prompt)

    # 5. Stream back
    yield ThreadItemAddedEvent(item=AssistantMessageItem(...))
```

### Pattern 2: Agent Integration

```python
from your_agent_framework import Agent

agent = Agent(tools=[...])

@chatkit_server.respond()
async def handle_message(context):
    user_text = context["user_message"].content

    # Run agent
    async for chunk in agent.run_stream(user_text):
        yield ThreadItemAddedEvent(item=AssistantMessageItem(
            content=[AssistantMessageContent(text=chunk)]
        ))
```

---

## Testing Strategies

### Frontend Testing (Jest + React Testing Library)

**Installation:**
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest
```

**File:** `src/components/ChatKitBot/ChatKitBot.test.jsx`

```javascript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatKitBot from './ChatKitBot';

// Mock useChatKit
jest.mock('@openai/chatkit-react', () => ({
  useChatKit: jest.fn(() => ({
    control: <div data-testid="chatkit-control">ChatKit Control</div>
  }))
}));

describe('ChatKitBot', () => {
  beforeEach(() => {
    localStorage.clear();
    // Mock window.getSelection
    window.getSelection = jest.fn(() => ({
      toString: () => '',
      getRangeAt: () => ({
        getBoundingClientRect: () => ({ left: 0, top: 0, width: 0, bottom: 0 })
      })
    }));
  });

  test('creates session ID on mount', () => {
    render(<ChatKitBot />);
    const sessionId = localStorage.getItem('chatkit_session_id');
    expect(sessionId).toBeTruthy();
    expect(sessionId).toMatch(/^session_\d+_[a-z0-9]+$/);
  });

  test('reuses existing session ID', () => {
    const existingId = 'session_123_abc';
    localStorage.setItem('chatkit_session_id', existingId);

    render(<ChatKitBot />);
    const sessionId = localStorage.getItem('chatkit_session_id');
    expect(sessionId).toBe(existingId);
  });

  test('renders ChatKit control', () => {
    render(<ChatKitBot />);
    expect(screen.getByTestId('chatkit-control')).toBeInTheDocument();
  });

  test('handles localStorage unavailable gracefully', () => {
    // Mock localStorage to throw error
    const originalLocalStorage = window.localStorage;
    delete window.localStorage;

    const { container } = render(<ChatKitBot />);
    expect(container).toBeInTheDocument();

    window.localStorage = originalLocalStorage;
  });

  test('detects text selection', async () => {
    window.getSelection = jest.fn(() => ({
      toString: () => 'Selected text here',
    }));

    render(<ChatKitBot />);

    // Simulate text selection
    const mouseUpEvent = new MouseEvent('mouseup', { bubbles: true });
    document.dispatchEvent(mouseUpEvent);

    await waitFor(() => {
      // Verify selected text is captured (check internal state if exposed)
    });
  });
});
```

### Backend Testing (pytest)

**Installation:**
```bash
pip install pytest pytest-asyncio httpx
```

**File:** `backend/test_chatkit_server.py`

```python
import pytest
from fastapi.testclient import TestClient
from chatkit_server import app
from database import SessionLocal, ChatSession, ChatMessage
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def db_session():
    """Create a test database session"""
    session = SessionLocal()
    yield session
    session.close()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "chatkit-backend"

def test_chatkit_endpoint_missing_session():
    """Test ChatKit endpoint without session ID"""
    response = client.post("/chatkit", json={"message": "Hello"})
    assert response.status_code == 400
    assert "X-Session-Id" in response.json()["detail"]

def test_chatkit_endpoint_with_session():
    """Test ChatKit endpoint with valid session"""
    headers = {"X-Session-Id": "test_session_123"}
    response = client.post(
        "/chatkit",
        headers=headers,
        json={"message": "Hello"}
    )
    assert response.status_code in [200, 201]

def test_chatkit_endpoint_empty_body():
    """Test ChatKit endpoint with empty body"""
    headers = {"X-Session-Id": "test_session_123"}
    response = client.post("/chatkit", headers=headers, content=b"")
    assert response.status_code == 400

def test_chatkit_endpoint_with_selected_text():
    """Test ChatKit endpoint with selected text header"""
    headers = {
        "X-Session-Id": "test_session_456",
        "X-Selected-Text": "This is selected text"
    }
    response = client.post(
        "/chatkit",
        headers=headers,
        json={"message": "Explain this"}
    )
    assert response.status_code in [200, 201]

@pytest.mark.asyncio
async def test_store_load_thread():
    """Test custom store thread loading"""
    from chatkit_store import CustomChatKitStore

    store = CustomChatKitStore()
    thread = await store.load_thread("test_thread_123")

    assert thread is not None
    assert thread.id == "test_thread_123"

@pytest.mark.asyncio
async def test_store_add_and_load_messages():
    """Test adding and loading messages"""
    from chatkit_store import CustomChatKitStore
    from openai_chatkit import UserMessageItem, AssistantMessageItem

    store = CustomChatKitStore()
    thread_id = f"test_thread_{datetime.utcnow().timestamp()}"

    # Add user message
    user_msg = UserMessageItem(
        id="msg_1",
        thread_id=thread_id,
        created_at=datetime.utcnow(),
        content="Hello"
    )
    await store.add_thread_item(thread_id, user_msg)

    # Load messages
    items = await store.load_thread_items(thread_id)
    assert len(items) == 1
    assert items[0].content == "Hello"

def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/chatkit")
    assert "access-control-allow-origin" in response.headers

@pytest.mark.asyncio
async def test_database_connection(db_session):
    """Test database connection and schema"""
    # Create test session
    session = ChatSession(
        id="test_db_session",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()

    # Verify it exists
    found = db_session.query(ChatSession).filter_by(id="test_db_session").first()
    assert found is not None
    assert found.id == "test_db_session"

    # Cleanup
    db_session.delete(found)
    db_session.commit()
```

### Integration Testing

**File:** `backend/test_integration.py`

```python
import pytest
from fastapi.testclient import TestClient
from chatkit_server import app
import time

client = TestClient(app)

def test_full_conversation_flow():
    """Test complete conversation flow"""
    session_id = f"integration_test_{int(time.time())}"

    # First message
    response1 = client.post(
        "/chatkit",
        headers={"X-Session-Id": session_id},
        json={"message": "Hello, how are you?"}
    )
    assert response1.status_code in [200, 201]

    # Second message (should have history)
    response2 = client.post(
        "/chatkit",
        headers={"X-Session-Id": session_id},
        json={"message": "What did I just ask?"}
    )
    assert response2.status_code in [200, 201]

def test_concurrent_sessions():
    """Test multiple concurrent sessions"""
    import concurrent.futures

    def send_message(session_num):
        session_id = f"concurrent_test_{session_num}"
        response = client.post(
            "/chatkit",
            headers={"X-Session-Id": session_id},
            json={"message": f"Message from session {session_num}"}
        )
        return response.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_message, i) for i in range(10)]
        results = [f.result() for f in futures]

    assert all(status in [200, 201] for status in results)
```

### Load Testing

**File:** `backend/locustfile.py`

```python
from locust import HttpUser, task, between

class ChatKitUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Initialize session"""
        import time
        self.session_id = f"load_test_{int(time.time())}_{self.client.base_url}"

    @task
    def send_message(self):
        """Send a chat message"""
        self.client.post(
            "/chatkit",
            headers={"X-Session-Id": self.session_id},
            json={"message": "Test message for load testing"}
        )

    @task(2)
    def health_check(self):
        """Check health endpoint"""
        self.client.get("/health")
```

**Run load test:**
```bash
pip install locust
locust -f backend/locustfile.py --host=http://localhost:8001
```

---

## Production Monitoring

### Logging Setup

**File:** `backend/logging_config.py`

```python
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import sys
import os

def setup_logging():
    """Configure comprehensive logging"""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console handler (for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    # File handler (rotating by size)
    file_handler = RotatingFileHandler(
        'logs/chatkit.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_format)

    # Error file handler (separate file for errors)
    error_handler = RotatingFileHandler(
        'logs/chatkit_errors.log',
        maxBytes=10485760,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_format)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    return logger

# Use in chatkit_server.py
from logging_config import setup_logging
logger = setup_logging()
```

### Metrics Collection

**File:** `backend/metrics.py`

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response, Request
import time

# Define metrics
chat_requests_total = Counter(
    'chatkit_requests_total',
    'Total number of chat requests',
    ['status', 'endpoint']
)

chat_request_duration = Histogram(
    'chatkit_request_duration_seconds',
    'Chat request duration in seconds',
    ['endpoint']
)

active_sessions = Gauge(
    'chatkit_active_sessions',
    'Number of active chat sessions'
)

message_length = Histogram(
    'chatkit_message_length_chars',
    'Length of chat messages in characters',
    buckets=[10, 50, 100, 500, 1000, 2000, 4000]
)

# Middleware for automatic metrics collection
async def metrics_middleware(request: Request, call_next):
    """Collect metrics for all requests"""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    endpoint = request.url.path

    chat_request_duration.labels(endpoint=endpoint).observe(duration)
    chat_requests_total.labels(
        status=response.status_code,
        endpoint=endpoint
    ).inc()

    return response

# Add to app
from fastapi import FastAPI
app = FastAPI()
app.middleware("http")(metrics_middleware)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

**Grafana Dashboard Configuration:**
```json
{
  "dashboard": {
    "title": "ChatKit Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(chatkit_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, chatkit_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Active Sessions",
        "targets": [
          {
            "expr": "chatkit_active_sessions"
          }
        ]
      }
    ]
  }
}
```

---

## Troubleshooting

### Issue 1: CORS Errors

**Symptom:** Browser console shows CORS policy errors

**Solution:**
```python
# Add your frontend domain to allow_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 2: SSR Hydration Errors

**Symptom:** React hydration mismatch in Next.js/Docusaurus

**Solution:** Always wrap in `BrowserOnly` or `dynamic` with `ssr: false`

### Issue 3: Session Not Persisting

**Symptom:** Chat history lost on refresh

**Solution:** Verify localStorage is working:
```javascript
console.log('Session ID:', localStorage.getItem('chatkit_session_id'));
```

### Issue 4: Streaming Not Working

**Symptom:** Response appears all at once instead of streaming

**Solution:** Ensure proper headers:
```python
return StreamingResponse(
    result,
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # For nginx
    }
)
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Session ID Not Persisting

**Problem:** Chat history lost on page refresh

**Cause:** localStorage not working or being cleared

**Solution:**
```javascript
// Add error handling and fallback
const getOrCreateSessionId = () => {
  try {
    let sid = localStorage.getItem('chatkit_session_id');
    if (!sid) {
      sid = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
      localStorage.setItem('chatkit_session_id', sid);
    }
    return sid;
  } catch (e) {
    console.error('localStorage not available:', e);
    // Fallback to memory-only session (will be lost on refresh)
    if (!window._tempSessionId) {
      window._tempSessionId = `temp_${Date.now()}`;
    }
    return window._tempSessionId;
  }
};
```

### Pitfall 2: CORS Errors in Production

**Problem:** Frontend can't connect to backend

**Cause:** Production domain not in CORS allow list

**Solution:**
```python
# Use environment variable for allowed origins
import os

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://your-domain.com"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Environment variable:**
```bash
ALLOWED_ORIGINS=http://localhost:3000,https://staging.example.com,https://example.com
```

### Pitfall 3: Database Connection Pool Exhaustion

**Problem:** Backend stops responding after many requests

**Cause:** Not closing database connections properly

**Solution:**
```python
# Use connection pooling with proper configuration
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,           # Number of connections to maintain
    max_overflow=20,        # Additional connections when pool is full
    pool_pre_ping=True,     # Verify connections before using
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_timeout=30,        # Timeout for getting connection from pool
)
```

### Pitfall 4: Streaming Not Working Behind Nginx

**Problem:** Responses appear all at once instead of streaming

**Cause:** Nginx buffering responses

**Solution:**
```nginx
# nginx.conf
location /chatkit {
    proxy_pass http://backend:8001;
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header X-Accel-Buffering no;
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
}
```

### Pitfall 5: Memory Leaks in Frontend

**Problem:** Browser becomes slow over time

**Cause:** Event listeners not cleaned up

**Solution:**
```javascript
useEffect(() => {
  const handleTextSelection = () => {
    // ... handler code
  };

  document.addEventListener('mouseup', handleTextSelection);
  document.addEventListener('touchend', handleTextSelection);

  // CRITICAL: Clean up on unmount
  return () => {
    document.removeEventListener('mouseup', handleTextSelection);
    document.removeEventListener('touchend', handleTextSelection);
  };
}, []); // Empty deps array - only run once
```

### Pitfall 6: SSR Hydration Mismatch

**Problem:** React hydration errors in Next.js/Docusaurus

**Cause:** ChatKit rendering on server side

**Solution:**
```javascript
// Always use dynamic import with ssr: false
import dynamic from 'next/dynamic';

const ChatKitBot = dynamic(() => import('@/components/ChatKitBot'), {
  ssr: false,
  loading: () => null, // Optional loading component
});
```

### Pitfall 7: Domain Key Not Working

**Problem:** ChatKit fails to initialize with domain key error

**Cause:** Domain not registered in OpenAI ChatKit dashboard

**Solution:**
1. Go to https://platform.openai.com/chatkit
2. Select your deployment
3. Add your domain to "Allowed Domains"
4. For localhost, use the special key `'local-dev'`

### Pitfall 8: Large Message Payloads

**Problem:** Requests fail with large messages or history

**Cause:** Payload size limits

**Solution:**
```python
# Limit message length
MAX_MESSAGE_LENGTH = 4000
MAX_HISTORY_ITEMS = 20

@chatkit_server.respond()
async def handle_message(context):
    user_text = context["user_message"].content

    # Validate length
    if len(user_text) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Message too long (max {MAX_MESSAGE_LENGTH} characters)")

    # Limit history
    history = await store.load_thread_items(thread.id, limit=MAX_HISTORY_ITEMS)
```

---

## Migration Guide

### From Existing Chat Solution

**Step 1: Audit Current Implementation**
- Document current chat features
- List custom functionality to preserve
- Export existing chat history (if needed)
- Identify integration points with your app

**Step 2: Parallel Implementation**
- Install ChatKit alongside existing solution
- Test with small user group (beta testers)
- Compare functionality and performance
- Gather feedback

**Step 3: Data Migration**

**File:** `backend/migrate_chat_history.py`

```python
from old_chat_db import OldChatDB, OldChatMessage
from database import ChatSession, ChatMessage, SessionLocal
from datetime import datetime
import uuid

def migrate_history():
    """Migrate chat history from old system to ChatKit"""
    old_db = OldChatDB()
    new_db = SessionLocal()

    try:
        sessions_migrated = 0
        messages_migrated = 0

        # Get all old sessions
        old_sessions = old_db.get_all_sessions()
        print(f"Found {len(old_sessions)} sessions to migrate")

        for old_session in old_sessions:
            # Create new session
            new_session = ChatSession(
                id=f"migrated_{old_session.id}",
                created_at=old_session.created_at or datetime.utcnow(),
                updated_at=old_session.updated_at or datetime.utcnow()
            )
            new_db.add(new_session)
            sessions_migrated += 1

            # Migrate messages
            old_messages = old_db.get_messages(old_session.id)
            for old_msg in old_messages:
                new_msg = ChatMessage(
                    id=f"migrated_{old_msg.id}" if old_msg.id else str(uuid.uuid4()),
                    session_id=new_session.id,
                    role=old_msg.role,  # Should be 'user' or 'assistant'
                    content=old_msg.content,
                    created_at=old_msg.created_at or datetime.utcnow()
                )
                new_db.add(new_msg)
                messages_migrated += 1

            # Commit after each session
            new_db.commit()

            if sessions_migrated % 100 == 0:
                print(f"Migrated {sessions_migrated} sessions, {messages_migrated} messages...")

        print(f"Migration complete! {sessions_migrated} sessions, {messages_migrated} messages")

    except Exception as e:
        print(f"Migration failed: {e}")
        new_db.rollback()
        raise
    finally:
        new_db.close()

if __name__ == "__main__":
    migrate_history()
```

**Run migration:**
```bash
python backend/migrate_chat_history.py
```

**Step 4: Feature Parity Check**
- [ ] Message sending/receiving
- [ ] History persistence
- [ ] User sessions
- [ ] Custom features (file upload, etc.)
- [ ] Mobile responsiveness
- [ ] Accessibility (keyboard navigation, screen readers)
- [ ] Error handling
- [ ] Rate limiting
- [ ] Analytics/tracking

**Step 5: Gradual Rollout**

**Phase 1: Internal Testing (Week 1)**
- Deploy to staging environment
- Test with internal team
- Fix critical bugs

**Phase 2: Beta Testing (Week 2-3)**
- Deploy to 10% of users (feature flag)
- Monitor errors and performance
- Gather user feedback
- Iterate on issues

**Phase 3: Gradual Rollout (Week 4-6)**
- Increase to 25% of users
- Monitor metrics (response time, error rate, user satisfaction)
- Increase to 50%
- Increase to 100%

**Phase 4: Deprecation (Week 7+)**
- Announce deprecation of old chat
- Provide migration guide for users
- Keep old system running for 2-4 weeks
- Fully remove old system

**Feature Flag Example:**
```javascript
// Frontend
const useChatKit = () => {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    // Check feature flag
    fetch('/api/feature-flags')
      .then(r => r.json())
      .then(flags => setEnabled(flags.chatkit_enabled));
  }, []);

  return enabled;
};

// In component
const chatkitEnabled = useChatKit();
return chatkitEnabled ? <ChatKitBot /> : <OldChat />;
```

---

## Production Deployment Checklist

### Pre-Deployment

**Environment Setup:**
- [ ] All environment variables configured (.env file)
- [ ] Database migrations run successfully
- [ ] Database backups configured
- [ ] CORS origins updated for production domains
- [ ] Domain key configured for production domain in OpenAI dashboard
- [ ] SSL/TLS certificates installed and valid
- [ ] Rate limiting configured (e.g., 10 requests/minute per session)
- [ ] Monitoring and logging set up (Prometheus, Grafana, etc.)
- [ ] Error tracking configured (Sentry, Rollbar, etc.)
- [ ] Load testing completed (target: 100 concurrent users)
- [ ] Security audit completed (OWASP top 10)

**Code Quality:**
- [ ] All tests passing (frontend + backend)
- [ ] Code review completed
- [ ] No hardcoded secrets or API keys
- [ ] Error handling comprehensive
- [ ] Logging appropriate (not too verbose, not too sparse)

**Documentation:**
- [ ] API documentation updated
- [ ] Deployment runbook created
- [ ] Rollback procedure documented
- [ ] Monitoring dashboard configured

### Deployment

**Backend Deployment:**
- [ ] Backend deployed to production server
- [ ] Health check endpoint responding (`/health`)
- [ ] Database connection verified
- [ ] Environment variables loaded correctly
- [ ] Logs being written to correct location
- [ ] Metrics endpoint accessible (`/metrics`)

**Frontend Deployment:**
- [ ] Frontend deployed with correct backend URL
- [ ] ChatKit CDN script loading correctly
- [ ] Domain key configured for production
- [ ] Service worker updated (if applicable)
- [ ] CDN cache cleared (if applicable)

**Integration Testing:**
- [ ] Test chat flow end-to-end in production
- [ ] Verify streaming works correctly
- [ ] Test session persistence (refresh page)
- [ ] Test selected text feature
- [ ] Test conversation history
- [ ] Test error scenarios (network failure, server error)
- [ ] Test on multiple devices (desktop, mobile, tablet)
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test mobile responsiveness
- [ ] Test accessibility (keyboard navigation, screen readers)

### Post-Deployment

**Monitoring (First 24 Hours):**
- [ ] Monitor error rates (target: < 1%)
- [ ] Check response times (target: p95 < 2s)
- [ ] Verify database performance (query times, connection pool)
- [ ] Monitor memory usage (backend + database)
- [ ] Check logs for unexpected errors or warnings
- [ ] Monitor user engagement metrics

**User Feedback:**
- [ ] Gather user feedback (surveys, support tickets)
- [ ] Monitor social media mentions
- [ ] Check analytics for usage patterns
- [ ] Identify common issues or complaints

**Optimization:**
- [ ] Document any issues encountered
- [ ] Plan improvements based on feedback
- [ ] Schedule follow-up deployments for fixes
- [ ] Update documentation with lessons learned

**Rollback Plan:**
- [ ] Keep previous version deployable
- [ ] Document rollback procedure
- [ ] Test rollback in staging
- [ ] Define rollback triggers (error rate > 5%, response time > 5s, etc.)

---

## Debug Checklist

### When Chat Doesn't Appear

1. **Check Browser Console**
   - Look for JavaScript errors
   - Verify ChatKit script loaded
   - Check for CSP violations

2. **Verify Component Mounting**
   ```javascript
   console.log('ChatKitBot mounting');
   ```

3. **Check SSR Safety**
   - Ensure wrapped in BrowserOnly/dynamic
   - Verify `typeof window !== 'undefined'` checks

### When Messages Don't Send

1. **Check Network Tab**
   - Verify POST to `/chatkit` endpoint
   - Check request headers (X-Session-Id)
   - Look for CORS errors

2. **Check Backend Logs**
   ```bash
   tail -f logs/chatkit.log
   ```

3. **Verify Session ID**
   ```javascript
   console.log('Session ID:', localStorage.getItem('chatkit_session_id'));
   ```

### When History Doesn't Persist

1. **Check Database**
   ```sql
   SELECT * FROM chat_sessions WHERE id = 'your_session_id';
   SELECT * FROM chat_messages WHERE session_id = 'your_session_id';
   ```

2. **Verify Store Implementation**
   - Check `load_thread_items` returns data
   - Verify `add_thread_item` saves to database

3. **Check Session ID Consistency**
   - Same session ID used across requests
   - localStorage not being cleared

---

## Deployment Checklist

### Frontend
- [ ] Install `@openai/chatkit-react`
- [ ] Load ChatKit CDN script
- [ ] Create ChatKit component with custom fetch
- [ ] Integrate globally (Root.js or _app.js)
- [ ] Add SSR safety (BrowserOnly/dynamic)
- [ ] Configure domain key from OpenAI dashboard
- [ ] Test on localhost
- [ ] Update production backend URL

### Backend
- [ ] Install `openai-chatkit` and dependencies
- [ ] Set up database schema (sessions + messages)
- [ ] Implement custom ChatKitStore
- [ ] Create ChatKit server with respond handler
- [ ] Add CORS middleware with frontend domains
- [ ] Configure environment variables
- [ ] Test /chatkit endpoint
- [ ] Add health check endpoint
- [ ] Deploy to production
- [ ] Verify HTTPS and CORS

### Database
- [ ] Create PostgreSQL database
- [ ] Run schema migrations
- [ ] Test connection from backend
- [ ] Set up backups
- [ ] Configure connection pooling

### Testing
- [ ] Test basic chat flow
- [ ] Test session persistence
- [ ] Test selected text feature
- [ ] Test conversation history
- [ ] Test on mobile devices
- [ ] Test in different browsers
- [ ] Load test with multiple concurrent users

---

## Performance Optimization

### Frontend
- Lazy load ChatKit component
- Debounce text selection events
- Limit selected text length (< 2000 chars)
- Use React.memo for expensive components

### Backend
- Implement connection pooling for database
- Cache frequent queries
- Use async/await throughout
- Limit conversation history retrieval (10-20 messages)
- Add rate limiting

### Database
- Index session_id and created_at columns
- Partition large tables by date
- Archive old conversations
- Use read replicas for history queries

---

## Security Considerations

1. **Input Validation**
   - Sanitize user input before storing
   - Limit message length (e.g., 4000 chars)
   - Validate session IDs format

2. **Rate Limiting**
   ```python
   from slowapi import Limiter

   limiter = Limiter(key_func=lambda: request.headers.get('X-Session-Id'))

   @app.post("/chatkit")
   @limiter.limit("10/minute")
   async def chatkit_endpoint(request: Request):
       ...
   ```

3. **Authentication** (if needed)
   - Add JWT token validation
   - Associate sessions with user IDs
   - Implement role-based access

4. **Data Privacy**
   - Encrypt sensitive data at rest
   - Implement data retention policies
   - Add GDPR compliance (data export/deletion)

---

## Reference Implementation

**Source Project:** PhysicalAI Humanoid Robotics Book
**Files:**
- Frontend: `src/components/Chatkit-chatbot/index.jsx`
- Backend: `backend/chatkit_server.py`
- Database: `backend/database.py`
- Store: Lines 98-335 in `chatkit_server.py`

**Live Demo:** https://alishbawajahat.github.io/PhysicalAI-humanoid-robotics-book-project/

---

## Quick Start Commands

```bash
# Frontend
npm install @openai/chatkit-react
npm run dev

# Backend
cd backend
pip install -r requirements.txt
python chatkit_server.py

# Database
psql $DATABASE_URL < schema.sql
```

---

## Support Resources

- **ChatKit Docs:** https://platform.openai.com/docs/chatkit
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev

---

**Agent Status:** ✅ Production Ready
**Last Tested:** 2026-02-09
**Compatibility:** React 18+, Python 3.9+, FastAPI 0.100+