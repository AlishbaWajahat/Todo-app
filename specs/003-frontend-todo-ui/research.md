# Technical Research: Frontend UI & Profile Integration

**Feature**: 003-frontend-todo-ui
**Date**: 2026-02-06
**Status**: Research Complete
**Purpose**: Document technical decisions for implementing JWT-based authentication, API integration, and UI patterns in Next.js 16 App Router

---

## Executive Summary

This document provides technical research and decisions for implementing a full-featured Todo application frontend using Next.js 16 App Router with JWT authentication. The research covers authentication strategies, API client architecture, route protection, state management, form handling, theme integration, and error handling patterns.

**Key Decisions**:
- **Authentication**: Better Auth with httpOnly cookies for JWT storage
- **API Client**: Centralized fetch wrapper with automatic JWT injection
- **Route Protection**: Next.js middleware for server-side authentication
- **State Management**: React Server Components with minimal client-side state
- **Forms**: HTML5 validation with progressive enhancement
- **Theme**: Tailwind CSS with existing purple/pink gradient palette
- **Error Handling**: Layered approach with global boundaries and component-level handling

---

## 1. Better Auth Integration Strategy

### Decision

Use **Better Auth** configured for JWT-based authentication with **httpOnly cookies** for token storage, integrated with Next.js 16 App Router middleware.

### Rationale

1. **Security-First**: httpOnly cookies prevent XSS attacks by making tokens inaccessible to JavaScript
2. **Automatic Token Management**: Cookies are sent automatically with every request
3. **Session Persistence**: Cookies persist across browser sessions
4. **Better Auth Compatibility**: Designed for Next.js with automatic JWT lifecycle management
5. **Backend Alignment**: Backend expects `Authorization: Bearer <token>` header

### Alternatives Considered

| Approach | Verdict | Reason |
|----------|---------|--------|
| localStorage | ❌ Rejected | Vulnerable to XSS attacks |
| sessionStorage | ❌ Rejected | Lost on page refresh |
| In-memory only | ❌ Rejected | Lost on page refresh |
| httpOnly cookies | ✅ Selected | XSS-safe, automatic, persistent |

### Implementation Notes

- Configure Better Auth with JWT secret matching backend
- Use httpOnly cookies with secure flag in production
- Implement automatic token refresh within updateAge window
- Handle 401 responses by redirecting to signin

### References

- [Better Auth Documentation](https://better-auth.com/docs)
- [OWASP JWT Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

---

## 2. API Client Architecture

### Decision

Implement a **centralized API client** using a fetch wrapper that automatically injects JWT tokens, handles errors consistently, and provides type-safe API functions.

### Rationale

1. **DRY Principle**: Single source of truth for API configuration
2. **Automatic Authentication**: JWT token automatically attached to all requests
3. **Type Safety**: TypeScript interfaces ensure correct request/response types
4. **Error Consistency**: Centralized error handling and transformation
5. **Backend Alignment**: Matches backend's expected format (Bearer token, JSON)

### Alternatives Considered

| Approach | Verdict | Reason |
|----------|---------|--------|
| Direct fetch calls | ❌ Rejected | Repetitive, error-prone |
| Axios library | ❌ Rejected | Unnecessary dependency |
| React Query | ❌ Rejected | Overkill for MVP |
| Custom fetch wrapper | ✅ Selected | Lightweight, type-safe, tailored |

### Implementation Pattern

**Base API Client**:
- Centralized `apiRequest<T>()` function
- Automatic JWT injection from Better Auth session
- Consistent error handling with ApiError class
- 401 handling with automatic redirect to signin
- Type-safe response parsing

**API Modules**:
- `taskApi`: CRUD operations for tasks
- `userApi`: Profile operations
- All functions return typed promises

### References

- [Fetch API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [TypeScript Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)

---

## 3. Route Protection Strategy

### Decision

Use **Next.js middleware** for server-side authentication checks on protected routes.

### Rationale

1. **Server-Side Security**: Authentication verified before page renders
2. **Performance**: Middleware runs at edge, faster than client-side checks
3. **SEO-Friendly**: Proper redirects for search engines
4. **Centralized Logic**: Single place to manage route protection

### Alternatives Considered

| Approach | Verdict | Reason |
|----------|---------|--------|
| Client-side only | ❌ Rejected | Flash of content, not secure |
| Layout-based | ❌ Rejected | Runs after page load |
| HOCs | ❌ Rejected | Client-side only |
| Next.js middleware | ✅ Selected | Server-side, fast, centralized |

### Implementation Pattern

**Middleware**:
- Check session for protected routes (`/dashboard`, `/tasks`, `/profile`)
- Redirect unauthenticated users to `/signin?redirect=<original-path>`
- Redirect authenticated users from auth pages to `/dashboard`
- Use matcher config to exclude static files and API routes

**Protected Layout**:
- Server-side session check in layout
- Provides user data to child components
- Includes app header with navigation

### References

- [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)
- [Next.js Authentication Guide](https://nextjs.org/docs/app/building-your-application/authentication)

---

## 4. State Management Approach

### Decision

Use **React Server Components** for data fetching with **minimal client-side state** (useState) for UI interactions. Use **React Context** only for truly global state (user session).

### Rationale

1. **Performance**: Server Components fetch data on server, reducing client bundle
2. **Simplicity**: No complex state management library needed
3. **Next.js Best Practices**: Leverage App Router's server-first architecture
4. **Type Safety**: TypeScript ensures correct data flow

### Alternatives Considered

| Approach | Verdict | Reason |
|----------|---------|--------|
| Redux/Redux Toolkit | ❌ Rejected | Heavy, complex, overkill |
| Zustand | ❌ Rejected | Not needed for MVP |
| Jotai/Recoil | ❌ Rejected | Learning curve |
| Server Components + useState | ✅ Selected | Simple, performant, native |

### Data Flow Pattern

1. **Server Component** fetches data on server (initial load)
2. **Client Component** receives data as props
3. **Local State** manages UI interactions (filtering, sorting)
4. **Optimistic Updates** for better UX (revert on error)
5. **Context** for truly global state (user session)

### When to Use Each

- **Server Component**: Data fetching, static content, SEO
- **Client Component**: Forms, interactive UI, event handlers
- **useState**: Local UI state (filters, modals, inputs)
- **Context**: Global state (user session, theme)

### References

- [Next.js Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [React useState](https://react.dev/reference/react/useState)

---

## 5. Form Handling & Validation

### Decision

Use **HTML5 native validation** with **custom error messages** and **progressive enhancement**. Backend validation remains the source of truth.

### Rationale

1. **No Dependencies**: Built into browsers
2. **Accessibility**: Works with screen readers
3. **Performance**: No JavaScript bundle overhead
4. **Progressive Enhancement**: Works without JavaScript
5. **Backend Alignment**: Backend validates, frontend provides early feedback

### Alternatives Considered

| Approach | Verdict | Reason |
|----------|---------|--------|
| React Hook Form | ❌ Rejected | Overkill for MVP |
| Formik | ❌ Rejected | Too complex |
| Zod + RHF | ❌ Rejected | Over-engineering |
| HTML5 validation | ✅ Selected | Native, accessible, lightweight |

### Implementation Pattern

**Form Validation**:
- Use HTML5 attributes: `required`, `minLength`, `maxLength`, `pattern`
- Custom error messages via `setCustomValidity()`
- Clear custom validity on input change
- Display backend validation errors from API responses
- Loading states during submission
- Optimistic updates where appropriate

**Error Handling**:
- Global errors displayed at form level
- Field-specific errors displayed inline
- ARIA attributes for accessibility (`aria-invalid`, `aria-describedby`)

### References

- [HTML5 Form Validation](https://developer.mozilla.org/en-US/docs/Learn/Forms/Form_validation)
- [ARIA Form Validation](https://www.w3.org/WAI/WCAG21/Techniques/aria/ARIA21)

---

## 6. Theme Integration

### Decision

Extend **Tailwind CSS configuration** with existing purple/pink gradient color palette and use utility classes for all styling.

### Rationale

1. **Preserve Existing Theme**: Maintains purple/pink gradient aesthetic
2. **Utility-First**: Tailwind's approach aligns with component-based architecture
3. **No Additional CSS**: All styling via Tailwind utilities
4. **Type Safety**: Tailwind IntelliSense provides autocomplete
5. **Responsive Design**: Built-in responsive utilities

### Color Palette

Existing colors to preserve:
- `#C5B0CD` - Light purple (primary-light)
- `#9B5DE0` - Medium purple (primary)
- `#450693` - Dark purple (primary-dark)
- `#FF2DD1` - Hot pink (accent-pink)
- `#F7A8C4` - Light pink (accent-light)

### Tailwind Configuration

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#C5B0CD',
          DEFAULT: '#9B5DE0',
          dark: '#450693',
        },
        accent: {
          pink: '#FF2DD1',
          light: '#F7A8C4',
        },
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(to bottom, #C5B0CD, #9B5DE0)',
      },
    },
  },
};
```

### Usage Patterns

- Background gradients: `bg-gradient-to-b from-[#C5B0CD] to-[#9B5DE0]`
- Primary buttons: `bg-primary hover:bg-primary-dark`
- Accent elements: `text-accent-pink`
- Cards: `bg-white shadow-lg rounded-lg`

### Responsive Breakpoints

- Mobile: `320px+` (default)
- Tablet: `md:` (768px+)
- Desktop: `lg:` (1024px+)

### References

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind Color Customization](https://tailwindcss.com/docs/customizing-colors)

---

## 7. Error Handling Patterns

### Decision

Implement **layered error handling** with global error boundaries, API client error handling, and component-level error states.

### Rationale

1. **Defense in Depth**: Multiple layers catch different error types
2. **User-Friendly**: Clear, actionable error messages
3. **Developer-Friendly**: Detailed logging for debugging
4. **Graceful Degradation**: App remains functional despite errors

### Error Handling Layers

**Layer 1: Global Error Boundary** (`app/error.tsx`):
- Catches unhandled React errors
- Displays generic error page
- Logs error details for debugging
- Provides "Try Again" button

**Layer 2: API Client** (`lib/api/client.ts`):
- Catches network errors
- Parses backend error responses
- Transforms to ApiError instances
- Handles 401 with automatic redirect

**Layer 3: Component-Level** (individual components):
- Displays specific error messages
- Provides retry mechanisms
- Shows loading states
- Handles form validation errors

**Layer 4: Toast Notifications** (transient errors):
- Non-blocking error messages
- Auto-dismiss after timeout
- Used for non-critical errors

### Error Message Guidelines

- **Be Specific**: "Task not found" not "Error occurred"
- **Be Actionable**: "Please try again" or "Check your connection"
- **Be Friendly**: Avoid technical jargon
- **Be Consistent**: Use same format across app

### Implementation Pattern

```typescript
// Global error boundary
export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold text-white mb-4">
        Something went wrong!
      </h2>
      <p className="text-white mb-4">
        {error.message || "An unexpected error occurred"}
      </p>
      <button onClick={reset} className="btn-primary">
        Try Again
      </button>
    </div>
  );
}
```

### References

- [Next.js Error Handling](https://nextjs.org/docs/app/building-your-application/routing/error-handling)
- [React Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)

---

## Summary of Decisions

| Topic | Decision | Key Benefit |
|-------|----------|-------------|
| Authentication | Better Auth + httpOnly cookies | XSS-safe, automatic |
| API Client | Centralized fetch wrapper | Type-safe, consistent |
| Route Protection | Next.js middleware | Server-side, fast |
| State Management | Server Components + useState | Simple, performant |
| Form Validation | HTML5 native | No dependencies |
| Theme | Tailwind CSS extended | Preserves existing design |
| Error Handling | Layered approach | Graceful degradation |

---

## Implementation Checklist

- [ ] Install Better Auth and configure with JWT settings
- [ ] Create API client with JWT injection
- [ ] Set up Next.js middleware for route protection
- [ ] Configure Tailwind with existing color palette
- [ ] Create base UI components (Button, Input, Card, etc.)
- [ ] Implement form validation patterns
- [ ] Set up error boundaries and error handling
- [ ] Test authentication flow end-to-end
- [ ] Verify theme consistency across all pages
- [ ] Test responsive design on mobile and desktop

---

**Research Complete**: All technical decisions documented and ready for implementation.
