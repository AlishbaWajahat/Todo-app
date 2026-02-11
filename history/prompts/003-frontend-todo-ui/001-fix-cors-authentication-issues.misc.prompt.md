---
id: 001
title: Fix CORS and Authentication Issues
stage: misc
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5
feature: 003-frontend-todo-ui
branch: 003-frontend-todo-ui
user: Alishba
command: debugging
labels: ["debugging", "cors", "authentication", "middleware", "cookies"]
links:
  spec: specs/003-frontend-todo-ui/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/middleware/auth.py
  - frontend/lib/api/auth.ts
  - backend/.env
  - backend/core/security.py
  - frontend/components/ui/Input.tsx
  - frontend/components/ui/Buttonnn.tsx
  - frontend/.env.local
tests:
  - Manual testing of signup flow
  - Manual testing of signin flow
  - Manual testing of CORS preflight requests
---

## Prompt

Test the complete frontend and backend application after implementation. Fix all issues preventing signup, signin, and API access including:
1. Button not visible on signup form
2. Signup returning unexpected errors
3. Signin not redirecting to dashboard
4. CORS errors on all API endpoints (tasks, users, auth)

## Response snapshot

Fixed multiple critical issues in the authentication and CORS flow:

1. **Python 3.13 bcrypt compatibility** (backend/core/security.py)
   - Replaced passlib with direct bcrypt usage
   - Added proper password truncation to 72 bytes
   - Implemented secure password hashing with salt rounds

2. **React hydration error** (frontend/components/ui/Input.tsx)
   - Replaced Math.random() with React's useId() hook
   - Fixed server/client ID mismatch causing hydration errors

3. **Button visibility** (frontend/components/ui/Buttonnn.tsx)
   - Updated with explicit hex colors (#9B5DE0)
   - Added borders and proper contrast for visibility

4. **CORS configuration** (backend/.env)
   - Added both ports 3000 and 3001 to CORS_ORIGINS
   - Enabled cross-origin requests from frontend

5. **Cookie-based authentication** (frontend/lib/api/auth.ts)
   - Changed from localStorage to cookies for token storage
   - Implemented setCookie/getCookie/deleteCookie helpers
   - Fixed Next.js middleware access to auth tokens

6. **CORS preflight handling** (backend/middleware/auth.py) - CRITICAL FIX
   - Added OPTIONS request bypass at beginning of auth_middleware
   - Allows CORS preflight requests to pass without authentication
   - Fixed 401 errors on all API endpoints

## Outcome

- ✅ Impact: Application now fully functional with working signup, signin, and authenticated API access
- 🧪 Tests: Manual testing of complete authentication flow and API endpoints
- 📁 Files: 7 files modified across frontend and backend
- 🔁 Next prompts: Test task creation, profile management, and full user workflows
- 🧠 Reflection: The CORS preflight issue was the root cause - OPTIONS requests don't include Authorization headers by design, so they must bypass authentication middleware

## Evaluation notes (flywheel)

- Failure modes observed:
  1. Python library compatibility with newer Python versions
  2. React SSR hydration mismatches from non-deterministic ID generation
  3. CORS preflight requests blocked by authentication middleware
  4. localStorage not accessible to Next.js middleware (server-side)

- Graders run and results (PASS/FAIL):
  - Signup flow: PASS
  - Signin flow: PASS
  - CORS preflight: PASS
  - Token persistence: PASS

- Prompt variant (if applicable): Iterative debugging with user feedback

- Next experiment (smallest change to try): Test complete user workflows including task CRUD operations and profile management
