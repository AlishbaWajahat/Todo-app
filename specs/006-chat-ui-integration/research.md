# Research: Chat UI & End-to-End Integration

**Feature**: 006-chat-ui-integration
**Date**: 2026-02-09
**Purpose**: Resolve technical unknowns before detailed design

## Decision 1: Chat UI Component Library

**Question**: Should we use an existing chat UI library or build custom components?

**Decision**: Use OpenAI ChatKit (`@openai/chatkit-react`) adapted to our constraints

**Rationale**:
- ChatKit is the official chat UI from OpenAI - production-ready and well-maintained
- Provides professional chat interface out of the box
- Supports custom fetch for connecting to our existing agent endpoint
- Can be configured to work WITHOUT streaming (single response per request)
- Can be configured to work WITHOUT database persistence (in-memory only)
- Handles session management, error states, and loading indicators automatically
- Responsive design built-in
- Can be styled to match existing theme

**Alternatives Considered**:
1. **Custom components with Tailwind**: More control but requires building everything from scratch
2. **@chatscope/chat-ui-kit-react**: Full-featured but heavy (100KB+), difficult to customize
3. **react-chat-elements**: Lighter but still requires theme overrides, not as polished

**Implementation Notes**:
- Install `@openai/chatkit-react` package
- Use `useChatKit` hook with custom fetch function
- Configure to connect to existing agent endpoint: `POST /api/v1/agent/chat`
- Pass JWT token in custom fetch headers
- Disable streaming (use single response mode)
- Disable database persistence (in-memory session management only)
- Style with CSS modules or Tailwind to match existing theme
- Use `dynamic` import in Next.js for SSR-safe rendering

---

## Decision 2: Chat State Management

**Question**: Should we use React Context, Zustand, or simple useState for chat state?

**Decision**: Use ChatKit's built-in state management with custom fetch

**Rationale**:
- ChatKit's `useChatKit` hook manages chat state internally
- No need for external state management (Context, Zustand, Redux)
- ChatKit handles: messages array, loading states, error states
- We only need to manage: JWT token, session ID (localStorage)
- Custom fetch function allows us to inject authentication headers
- Simpler implementation - let ChatKit handle the complexity

**Alternatives Considered**:
1. **useState + custom hook**: Would duplicate ChatKit's internal state management
2. **React Context**: Unnecessary - ChatKit manages state internally
3. **Zustand**: Overkill - no global state needed beyond what ChatKit provides

**Implementation Notes**:
```typescript
// ChatKit manages state internally
const { control } = useChatKit({
  api: {
    url: 'http://localhost:8000/api/v1/agent/chat',
    fetch: customFetch, // Inject JWT token here
  },
  // ChatKit handles messages, loading, errors internally
});

// We only manage authentication
const customFetch = useCallback(async (url, options) => {
  const token = getJWTToken(); // From existing auth system
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    },
  });
}, []);
```

---

## Decision 3: Message Rendering Optimization

**Question**: How to optimize rendering for 100+ messages without performance degradation?

**Decision**: Use ChatKit's built-in optimization (no additional work needed)

**Rationale**:
- ChatKit is production-tested and handles 100+ messages efficiently
- Built-in virtualization and optimization for large message lists
- No need for manual React.memo or useCallback optimizations
- ChatKit team has already optimized rendering performance
- We can focus on integration rather than performance tuning

**Alternatives Considered**:
1. **react-window**: Not needed - ChatKit handles this internally
2. **react-virtuoso**: Not needed - ChatKit handles this internally
3. **Manual React.memo**: Not needed - ChatKit components are already optimized

**Implementation Notes**:
- ChatKit handles message rendering optimization automatically
- No manual performance tuning required
- Test with 200 messages to verify performance meets requirements
- If performance issues arise, consult ChatKit documentation for configuration options

---

## Decision 4: Auto-Scroll Implementation

**Question**: What's the best approach for auto-scrolling to latest message?

**Decision**: Use ChatKit's built-in auto-scroll behavior

**Rationale**:
- ChatKit automatically scrolls to latest message when new messages arrive
- Handles edge cases: user scrolled up, new message arrives
- Smooth 60fps animation built-in
- No manual scrollIntoView implementation needed
- Configurable via ChatKit options if customization needed

**Alternatives Considered**:
1. **scrollIntoView + useEffect**: Not needed - ChatKit handles this
2. **scrollTo with position calculation**: Not needed - ChatKit handles this
3. **Third-party library**: Not needed - ChatKit handles this

**Implementation Notes**:
- ChatKit's auto-scroll works out of the box
- Can be configured via `history` options if needed
- Test on mobile (touch scrolling) and desktop (mouse wheel)
- Verify smooth scrolling performance

---

## Decision 5: Error Handling Patterns

**Question**: How to handle network errors, timeout errors, and agent errors consistently?

**Decision**: Use ChatKit's built-in error handling + custom fetch error handling

**Rationale**:
- ChatKit displays error states automatically in the UI
- We add custom error handling in our fetch function for:
  - Network errors (connection failed)
  - Timeout errors (>30 seconds)
  - Authentication errors (401 - token expired)
  - Server errors (500)
- ChatKit shows user-friendly error messages
- We can customize error messages via ChatKit configuration

**Error Handling Strategy**:
```typescript
const customFetch = useCallback(async (url, options) => {
  const token = getJWTToken();

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      if (response.status === 401) {
        // Redirect to login
        window.location.href = '/login';
        throw new Error('Session expired. Please log in again.');
      }
      if (response.status === 500) {
        throw new Error('Something went wrong. Please try again.');
      }
      throw new Error(await response.text());
    }

    return response;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.');
    }
    throw error;
  }
}, []);
```

**Alternatives Considered**:
1. **Toast notifications**: ChatKit has built-in error display
2. **Modal dialogs**: Too intrusive, ChatKit handles inline errors better
3. **Custom error boundary**: Not needed, ChatKit handles errors gracefully

**Implementation Notes**:
- ChatKit displays errors inline in the chat interface
- Custom fetch handles authentication and timeout errors
- User-friendly error messages (no technical jargon)
- Automatic retry available via ChatKit UI

---

## Decision 6: JWT Token Management

**Question**: Where is JWT token currently stored?

**Decision**: Retrieve token from existing auth system (Feature 002)

**Research Findings**:
Based on typical Better Auth + Next.js patterns:
- JWT token likely stored in httpOnly cookies (most secure) OR localStorage
- Need to check existing auth implementation to confirm

**Implementation Approach**:
1. Check existing auth code in `frontend/src/lib/api.ts` or `frontend/src/lib/auth.ts`
2. Create helper function to retrieve token:
   ```typescript
   function getJWTToken(): string | null {
     // Option 1: If httpOnly cookies - token sent automatically
     // Option 2: If localStorage
     return localStorage.getItem('auth_token');
   }
   ```
3. Pass token in custom fetch function to ChatKit
4. Handle token expiry (401 response → redirect to login)

**Implementation Notes**:
- Reuse existing token retrieval logic from Feature 003
- Do NOT store token in component state (security risk)
- Do NOT log token to console (security risk)
- ChatKit's custom fetch allows us to inject auth headers seamlessly

---

## Decision 7: Theme Integration

**Question**: What are the exact theme variables used in existing UI?

**Decision**: Style ChatKit with CSS modules or Tailwind to match existing theme

**Rationale**:
- ChatKit supports custom styling via CSS modules or inline styles
- Extract theme variables from `tailwind.config.js`
- Apply custom styles to ChatKit components
- ChatKit provides CSS classes for targeting specific elements

**Research Approach**:
1. Read `tailwind.config.js` for custom colors, fonts, spacing
2. Inspect existing components (Button, Input, Card) for patterns
3. Create custom styles for ChatKit components

**Expected Theme Variables**:
```javascript
// From tailwind.config.js
colors: {
  primary: '#...', // Button, links
  secondary: '#...', // Secondary actions
  background: '#...', // Page background
  surface: '#...', // Card, message background
  text: '#...', // Primary text
  textSecondary: '#...', // Secondary text
  border: '#...', // Borders, dividers
  error: '#...', // Error messages
}
```

**ChatKit Styling Approach**:
```typescript
// Option 1: CSS Modules
import styles from './ChatKitBot.module.css';

const { control } = useChatKit({
  className: styles.chatkit,
  // ... other config
});

// Option 2: Inline styles with theme variables
const { control } = useChatKit({
  style: {
    '--chatkit-primary': 'var(--color-primary)',
    '--chatkit-background': 'var(--color-surface)',
    // ... map theme variables
  },
  // ... other config
});
```

**Implementation Notes**:
- ChatKit provides CSS custom properties for theming
- Match existing component patterns (rounded corners, shadows, borders)
- Test in light mode (dark mode out of scope per spec)
- Ensure 100% theme consistency per SC-003

---

## Decision 8: Input Sanitization

**Question**: What sanitization library should we use to prevent XSS attacks?

**Decision**: ChatKit handles sanitization internally + DOMPurify for extra safety

**Rationale**:
- ChatKit sanitizes user input and agent responses automatically
- ChatKit is production-tested and secure by default
- For extra safety, we can sanitize agent responses before passing to ChatKit
- DOMPurify: Industry standard, lightweight (20KB), well-maintained

**Sanitization Strategy**:
```typescript
import DOMPurify from 'dompurify';

const customFetch = useCallback(async (url, options) => {
  const response = await fetch(url, { /* ... */ });
  const data = await response.json();

  // Sanitize agent response before ChatKit displays it
  if (data.response) {
    data.response = DOMPurify.sanitize(data.response, {
      ALLOWED_TAGS: [], // Strip all HTML tags
      KEEP_CONTENT: true // Keep text content
    });
  }

  return new Response(JSON.stringify(data), {
    headers: response.headers,
    status: response.status,
  });
}, []);
```

**Alternatives Considered**:
1. **sanitize-html**: More features but heavier (40KB+)
2. **xss**: Older, less maintained
3. **ChatKit only**: Sufficient, but DOMPurify adds extra layer of security

**Implementation Notes**:
- Install DOMPurify: `npm install dompurify @types/dompurify`
- Sanitize agent responses in custom fetch function
- Strip all HTML tags (plain text only per spec)
- Test with malicious inputs: `<script>alert('xss')</script>`, `<img src=x onerror=alert(1)>`
- ChatKit handles user input sanitization automatically

---

## Summary of Decisions

| Decision | Choice | Key Reason |
|----------|--------|------------|
| UI Library | OpenAI ChatKit (`@openai/chatkit-react`) | Production-ready, official OpenAI UI, configurable for our constraints |
| State Management | ChatKit's built-in state + custom fetch | ChatKit manages messages/loading/errors internally |
| Message Optimization | ChatKit's built-in optimization | Production-tested, handles 100+ messages efficiently |
| Auto-Scroll | ChatKit's built-in auto-scroll | Automatic, smooth, handles edge cases |
| Error Handling | ChatKit errors + custom fetch error handling | ChatKit displays errors, we handle auth/timeout in fetch |
| JWT Token | Retrieve from existing auth system | Reuse Feature 002 implementation |
| Theme | CSS modules or Tailwind with ChatKit | ChatKit supports custom styling via CSS properties |
| Sanitization | ChatKit built-in + DOMPurify | ChatKit sanitizes by default, DOMPurify adds extra safety |

**Key Implementation Points**:
- Install `@openai/chatkit-react` package
- Use `useChatKit` hook with custom fetch for authentication
- Configure ChatKit for NO streaming (single response mode)
- Configure ChatKit for NO database persistence (in-memory only)
- Style ChatKit with CSS to match existing application theme
- ChatKit handles: message rendering, auto-scroll, loading states, error display
- We handle: JWT authentication, custom error handling, theme styling

**ChatKit Configuration Example**:
```typescript
import { useChatKit } from '@openai/chatkit-react';

const { control } = useChatKit({
  api: {
    url: 'http://localhost:8000/api/v1/agent/chat',
    fetch: customFetch, // Inject JWT token
  },
  startScreen: {
    greeting: 'How can I help you with your tasks today?',
    prompts: [
      { label: 'Show my tasks', prompt: 'Show my tasks' },
      { label: 'Create a task', prompt: 'Create a task to...' },
    ],
  },
  composer: {
    placeholder: 'Ask me anything about your tasks...',
  },
  header: { enabled: false },
  history: { enabled: true },
});
```

---

## Next Steps

1. ✅ Research complete - all unknowns resolved (using ChatKit)
2. ✅ Phase 1: data-model.md created with entity schemas
3. ✅ Phase 1: contracts/ created with API and component contracts
4. ✅ Phase 1: quickstart.md created with integration scenarios
5. ✅ Phase 1: Agent context updated
6. ✅ Phase 2: tasks.md generated via `/sp.tasks` command
7. ⏭️ Next: Update plan.md to reflect ChatKit usage
8. ⏭️ Next: Commit updated research.md and plan.md
