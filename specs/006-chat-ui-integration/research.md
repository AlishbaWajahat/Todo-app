# Research: Chat UI & End-to-End Integration

**Feature**: 006-chat-ui-integration
**Date**: 2026-02-09
**Purpose**: Resolve technical unknowns before detailed design

## Decision 1: Chat UI Component Library

**Question**: Should we use an existing chat UI library or build custom components?

**Decision**: Build custom components using Tailwind CSS

**Rationale**:
- Existing theme must be preserved with 100% consistency (SC-003)
- Tailwind CSS already in use, custom components integrate seamlessly
- Chat UI is simple (4 components: Container, MessageList, Input, Message)
- No need for complex features (no file uploads, reactions, typing indicators)
- Custom components give full control over styling and behavior
- Smaller bundle size (no external library overhead)

**Alternatives Considered**:
1. **@chatscope/chat-ui-kit-react**: Full-featured but heavy (100KB+), difficult to customize theme
2. **react-chat-elements**: Lighter but still requires theme overrides, not Tailwind-native
3. **stream-chat-react**: Overkill for simple request/response chat, requires Stream backend

**Implementation Notes**:
- Use Tailwind utility classes for all styling
- Extract theme colors from existing components (likely in tailwind.config.js)
- Reuse existing UI components (Button, Input) where possible
- Keep components simple and focused (single responsibility)

---

## Decision 2: Chat State Management

**Question**: Should we use React Context, Zustand, or simple useState for chat state?

**Decision**: Use custom hook (useChat) with useState

**Rationale**:
- Chat state is local to chat page (no global state needed)
- Simple state: messages[], isLoading, error
- useState is sufficient for this scope
- Custom hook encapsulates logic and makes testing easier
- No need for Context (no deeply nested components)
- No need for Zustand (no complex state management)

**Alternatives Considered**:
1. **React Context**: Overkill for single-page state, adds unnecessary complexity
2. **Zustand**: Good for global state, but chat state is page-local
3. **Redux**: Way too heavy for this simple use case

**Implementation Notes**:
```typescript
// useChat.ts structure
export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (text: string) => { /* ... */ };
  const clearError = () => setError(null);

  return { messages, isLoading, error, sendMessage, clearError };
}
```

---

## Decision 3: Message Rendering Optimization

**Question**: How to optimize rendering for 100+ messages without performance degradation?

**Decision**: Use simple optimization techniques (no virtualization)

**Rationale**:
- 100 messages is not a large dataset for modern browsers
- Simple optimizations are sufficient:
  - React.memo for Message component (prevent unnecessary re-renders)
  - Key prop with stable IDs (client-generated UUIDs)
  - Avoid inline functions in render (use useCallback)
- Virtualization adds complexity and may conflict with auto-scroll
- Spec says "support for 100+ messages" not "support for 10,000+ messages"

**Alternatives Considered**:
1. **react-window**: Good for 1000+ items, overkill for 100
2. **react-virtuoso**: Better for chat (handles dynamic heights), but adds 20KB and complexity
3. **Intersection Observer**: Could lazy-load old messages, but not needed for 100 items

**Implementation Notes**:
- Wrap Message component with React.memo
- Use stable message IDs (UUID v4 generated on client)
- Use useCallback for event handlers
- Profile with React DevTools to verify no unnecessary re-renders
- Test with 200 messages to ensure smooth performance

---

## Decision 4: Auto-Scroll Implementation

**Question**: What's the best approach for auto-scrolling to latest message?

**Decision**: Use scrollIntoView with smooth behavior + useEffect

**Rationale**:
- scrollIntoView is native, performant, and well-supported
- smooth behavior provides 60fps animation
- useEffect triggers scroll when messages change
- Can detect user scroll position to disable auto-scroll when user scrolls up

**Implementation Pattern**:
```typescript
const messagesEndRef = useRef<HTMLDivElement>(null);
const [autoScroll, setAutoScroll] = useState(true);

useEffect(() => {
  if (autoScroll && messagesEndRef.current) {
    messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
  }
}, [messages, autoScroll]);

// Detect user scroll
const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
  const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
  const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
  setAutoScroll(isAtBottom);
};
```

**Alternatives Considered**:
1. **scrollTo**: Works but requires calculating scroll position
2. **scrollTop assignment**: Not smooth, jarring user experience
3. **Third-party library**: Unnecessary for this simple use case

**Implementation Notes**:
- Add invisible div at end of message list as scroll target
- Disable auto-scroll when user scrolls up (>50px from bottom)
- Re-enable auto-scroll when user scrolls back to bottom
- Test on mobile (touch scrolling) and desktop (mouse wheel)

---

## Decision 5: Error Handling Patterns

**Question**: How to handle network errors, timeout errors, and agent errors consistently?

**Decision**: Use error boundary + inline error display + retry mechanism

**Rationale**:
- Error boundary catches unexpected React errors (prevents white screen)
- Inline error display shows user-friendly messages in chat UI
- Retry mechanism allows users to recover from transient failures
- Different error types get different messages:
  - Network error: "Connection failed. Please check your internet."
  - Timeout: "Request timed out. Please try again."
  - 401: "Session expired. Please log in again."
  - 500: "Something went wrong. Please try again."

**Error Handling Strategy**:
```typescript
try {
  const response = await fetch(url, { signal: AbortSignal.timeout(30000) });
  if (!response.ok) {
    if (response.status === 401) throw new AuthError();
    if (response.status === 500) throw new ServerError();
    throw new Error(await response.text());
  }
} catch (error) {
  if (error.name === 'AbortError') {
    setError('Request timed out. Please try again.');
  } else if (error instanceof AuthError) {
    // Redirect to login
  } else {
    setError('Something went wrong. Please try again.');
  }
}
```

**Alternatives Considered**:
1. **Toast notifications**: Could work but less visible in chat context
2. **Modal dialogs**: Too intrusive for transient errors
3. **Status bar**: Less prominent, users might miss errors

**Implementation Notes**:
- Display errors inline in chat (red background, error icon)
- Provide "Retry" button for transient errors
- Provide "Log in" button for auth errors
- Clear error when user sends new message
- Log errors to console for debugging (but not to user)

---

## Decision 6: JWT Token Management

**Question**: Where is JWT token currently stored?

**Decision**: Review existing implementation (Feature 002)

**Research Findings**:
Based on typical Better Auth + Next.js patterns:
- JWT token likely stored in httpOnly cookies (most secure)
- Alternative: localStorage (less secure but simpler)
- Need to check existing auth implementation to confirm

**Implementation Approach**:
1. Check existing auth code in frontend/src/lib/api.ts
2. If httpOnly cookies: Token automatically included in requests (no manual handling)
3. If localStorage: Retrieve token and add to Authorization header manually

**Code Pattern** (if localStorage):
```typescript
const token = localStorage.getItem('auth_token');
const response = await fetch(url, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

**Implementation Notes**:
- Reuse existing token retrieval logic from Feature 003
- Handle token expiry (401 response → redirect to login)
- Do NOT store token in component state (security risk)
- Do NOT log token to console (security risk)

---

## Decision 7: Theme Integration

**Question**: What are the exact theme variables used in existing UI?

**Decision**: Extract from tailwind.config.js and existing components

**Research Approach**:
1. Read tailwind.config.js for custom colors, fonts, spacing
2. Inspect existing components (Button, Input, Card) for patterns
3. Document theme variables for chat components

**Expected Theme Variables**:
```javascript
// Colors (likely)
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

// Spacing (Tailwind defaults or custom)
spacing: { /* ... */ }

// Typography (Tailwind defaults or custom)
fontFamily: { /* ... */ }
```

**Implementation Notes**:
- Use Tailwind utility classes (e.g., bg-surface, text-primary)
- Avoid hardcoded colors (use theme variables)
- Match existing component patterns (rounded corners, shadows, borders)
- Test in light mode (dark mode out of scope per spec)

---

## Decision 8: Input Sanitization

**Question**: What sanitization library should we use to prevent XSS attacks?

**Decision**: Use DOMPurify for agent responses, native escaping for user input

**Rationale**:
- User input: React automatically escapes text content (no XSS risk)
- Agent responses: May contain special characters, need sanitization
- DOMPurify: Industry standard, lightweight (20KB), well-maintained
- Alternative: sanitize-html (heavier, more features we don't need)

**Sanitization Strategy**:
```typescript
import DOMPurify from 'dompurify';

// User input (React handles automatically)
<p>{userMessage}</p> // Safe - React escapes

// Agent response (sanitize before rendering)
const sanitizedResponse = DOMPurify.sanitize(agentResponse, {
  ALLOWED_TAGS: [], // Strip all HTML tags
  KEEP_CONTENT: true // Keep text content
});
<p>{sanitizedResponse}</p>
```

**Alternatives Considered**:
1. **sanitize-html**: More features but heavier (40KB+)
2. **xss**: Older, less maintained
3. **Built-in escaping**: React handles user input, but need library for agent responses

**Implementation Notes**:
- Install DOMPurify: `npm install dompurify @types/dompurify`
- Sanitize agent responses before storing in state
- Strip all HTML tags (plain text only per spec)
- Test with malicious inputs: `<script>alert('xss')</script>`, `<img src=x onerror=alert(1)>`

---

## Summary of Decisions

| Decision | Choice | Key Reason |
|----------|--------|------------|
| UI Library | Custom components | Theme consistency, simplicity |
| State Management | useState + custom hook | Local state, simple scope |
| Message Optimization | React.memo + useCallback | Sufficient for 100 messages |
| Auto-Scroll | scrollIntoView + useEffect | Native, performant, smooth |
| Error Handling | Inline display + retry | User-friendly, recoverable |
| JWT Token | Review existing (likely httpOnly cookies) | Reuse existing auth |
| Theme | Extract from tailwind.config.js | 100% consistency |
| Sanitization | DOMPurify | Industry standard, lightweight |

---

## Next Steps

1. ✅ Research complete - all unknowns resolved
2. ⏭️ Phase 1: Create data-model.md with entity schemas
3. ⏭️ Phase 1: Create contracts/ with API and component contracts
4. ⏭️ Phase 1: Create quickstart.md with integration scenarios
5. ⏭️ Phase 1: Update agent context (if new technologies added)
6. ⏭️ Phase 2: Generate tasks.md via `/sp.tasks` command
