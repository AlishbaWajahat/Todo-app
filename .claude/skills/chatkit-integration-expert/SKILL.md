---
name: "chatbot-developer"
description: "Integrate OpenAI ChatKit React floating overlay widget with a FastAPI backend agent endpoint. Covers ChatKit Python Server SDK adapter, JWT-authenticated custom fetch, next-themes dark/light theming, text selection context menu, session persistence, and collapsible widget."
version: "4.0.0"
---

# ChatKit Floating Widget + FastAPI Agent Integration Skill

> **IMPORTANT:** For comprehensive troubleshooting and all known pitfalls, see the
> `chatkit-integration-expert` agent in `.claude/agents/chatkit-integration-expert.md`.
> This skill provides the implementation templates; the agent provides diagnostics.

## When to Use This Skill

- User wants to "add a chat widget to the app" or "embed a chatbot overlay"
- User needs a floating ChatKit React widget connected to an existing FastAPI AI agent backend
- User wants JWT-authenticated chat with dark/light theming and text selection support
- User needs a ChatKit Python Server SDK adapter wrapping an existing AI agent

## Architecture

```
User -> Floating ChatKit Widget -> POST /chatkit (ChatKit SSE protocol)
                                         |
                                   FastAPI endpoint
                                         |
                                   Extract JWT -> Validate -> Get user_id (UUID)
                                         |
                                   ChatKitServer.process(payload, context)
                                         |
                                   ChatKitServer.respond() -> Agent + MCP tools
                                         |
                                   SSE Stream -> ChatKit Widget -> User sees response
```

## Critical Requirements (DO NOT SKIP)

### 1. CDN Script in Layout (MANDATORY)
The `<openai-chatkit>` web component is NOT included in the npm package. It MUST be loaded from OpenAI's CDN:

```tsx
// app/layout.tsx
import Script from "next/script";

// Inside <body>:
<Script
  src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
  strategy="lazyOnload"
/>
```

Without this, ChatKit silently fails — no errors, no logs, nothing renders.

### 2. JWT Authentication via Custom Fetch (MANDATORY)
ChatKit uses its own internal fetch. You MUST provide a custom fetch to include JWT tokens:

```typescript
const authenticatedFetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  const token = getToken();
  const headers = new Headers(init?.headers);
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return fetch(input, { ...init, headers });
};

const { control } = useChatKit({
  api: {
    url: `${apiBaseUrl}/chatkit`,
    domainKey: 'your_domain_key',
    fetch: authenticatedFetch,  // REQUIRED for JWT
  },
});
```

### 3. Correct JWT Decode in Backend (VERIFY IMPORT PATH)
Find your project's `decode_access_token` function and use the correct import:

```python
# Find the function:
# grep -rn "def decode_access_token" backend/src/

# Common locations:
from src.core.security import decode_access_token  # This project
# NOT: from src.auth.jwt import decode_access_token (WRONG)

# CRITICAL: It returns a tuple (payload, error), not just payload:
payload, error = decode_access_token(token)
if payload:
    user_id = payload.get("sub", "anonymous")
```

### 4. Agent vs RunResult (CRITICAL)
`Runner.run_streamed()` expects an `Agent` object, NOT a `RunResult`:

```python
# WRONG — causes 'RunResult has no attribute output_type':
result = Runner.run_streamed(await run_agent(user_id, text, []), input=text)

# CORRECT — create Agent inline:
async with MCPServerStreamableHttp(name="MCP", params={"url": MCP_URL}) as server:
    agent = Agent(name="Assistant", instructions=..., mcp_servers=[server], model="gpt-4o-mini")
    result = Runner.run_streamed(agent, input=text)
```

### 5. ChatKit Store Types (MUST USE CORRECT TYPES)
```python
from chatkit.store import Store
from chatkit.types import ThreadMetadata, ThreadItem, Page

class MemoryStore(Store[dict]):  # Generic with context type
    # All methods must use ThreadMetadata, ThreadItem, Page[T]
```

## Implementation Order

1. **Backend Store**: `backend/app/chatkit_store.py` — MemoryStore with all 14 methods
2. **Backend Server**: `backend/app/chatkit_server.py` — ChatKitServer with inline Agent + MCP
3. **Backend Endpoint**: Update `main.py` — `/chatkit` POST endpoint with JWT decode
4. **Frontend CDN**: Add ChatKit CDN script to `app/layout.tsx`
5. **Frontend Widget**: `components/ChatKitWidget.tsx` with authenticated fetch
6. **Frontend Mount**: Mount `<ChatKitWidget />` in layout

## Deliverables

### Backend Files

| File | Purpose |
|------|---------|
| `backend/app/chatkit_store.py` | MemoryStore extending `Store[dict]` with 14 methods |
| `backend/app/chatkit_server.py` | ChatKitServer with inline Agent + MCPServerStreamableHttp |
| `backend/main.py` | `/chatkit` endpoint with correct JWT decode (update) |
| `backend/requirements.txt` | `openai-chatkit`, `openai-agents` (update) |

### Frontend Files

| File | Purpose |
|------|---------|
| `frontend/app/layout.tsx` | CDN script + mount ChatKitWidget (update) |
| `frontend/components/ChatKitWidget.tsx` | Floating widget with JWT fetch, conditional rendering |
| `frontend/components/TextSelectionMenu.tsx` | Text selection "Ask from AI" context menu |
| `frontend/package.json` | `@openai/chatkit-react` (update) |

## Verified Technology Versions

| Package | Version |
|---------|---------|
| `@openai/chatkit-react` | 1.4.3 |
| `@openai/chatkit` (types only) | 1.5.0 |
| `openai-chatkit` (Python) | latest |
| `openai-agents` (Python) | latest |
| Next.js | 16+ |
| React | 19+ |
| FastAPI | 0.109+ |


```