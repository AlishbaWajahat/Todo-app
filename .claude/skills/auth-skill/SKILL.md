---
name: auth-skill
description: Implement Better Auth on frontend and JWT token verification in FastAPI backend for secure authentication.
---

# Authentication with Better Auth & FastAPI JWT

**Tech Stack:** Better Auth (Frontend) + FastAPI JWT Verification (Backend)

## Instructions

1. **Better Auth Frontend Setup (Next.js)**
   - Install and configure Better Auth in Next.js
   - Set up authentication providers (email/password)
   - Configure JWT token generation
   - Implement signup and signin pages
   - Store JWT tokens securely (HTTP-only cookies or secure storage)
   - Add authentication context/provider for app-wide access

2. **JWT Token Flow**
   - User signs up/signs in via Better Auth on frontend
   - Better Auth generates and returns JWT token
   - Frontend stores token securely
   - Frontend includes token in API requests: `Authorization: Bearer <token>`
   - Backend verifies token signature and extracts user claims
   - Backend filters data based on authenticated user ID

3. **FastAPI Backend JWT Verification**
   - Install python-jose for JWT handling
   - Create JWT verification dependency
   - Extract token from Authorization header
   - Verify token signature using shared secret
   - Decode token to get user ID and claims
   - Validate token expiration
   - Return 401 Unauthorized for invalid/expired tokens

4. **Protected Routes & Endpoints**
   - Add JWT verification dependency to protected FastAPI routes
   - Extract current user from verified token
   - Filter database queries by authenticated user ID
   - Ensure users can only access their own data
   - Implement proper authorization checks

5. **Security Best Practices**
   - Use HTTPS only in production
   - Store JWT secret in environment variables
   - Set appropriate token expiration times
   - Validate all authentication inputs
   - Handle authentication errors gracefully
   - Implement rate limiting on auth endpoints
   - Never expose sensitive data in JWT payload

## Best Practices
- Use HTTPS for all authentication flows
- Store JWT secrets securely in .env files
- Set reasonable token expiration (15min-1hr for access tokens)
- Implement token refresh mechanism if needed
- Validate tokens on every protected request
- Use HTTP-only cookies for token storage when possible
- Handle expired tokens gracefully with clear error messages
- Filter all data queries by authenticated user ID
- Never trust client-side data; always verify on backend

## Example Structure

### Frontend (Next.js with Better Auth)

```tsx
// lib/auth.ts - Better Auth Configuration
import { betterAuth } from 'better-auth'

export const auth = betterAuth({
  secret: process.env.AUTH_SECRET,
  database: {
    // Database configuration
  },
  emailAndPassword: {
    enabled: true,
  },
})

// app/login/page.tsx - Login Page
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()

    try {
      const response = await fetch('/api/auth/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (response.ok) {
        const { token } = await response.json()
        // Store token securely
        localStorage.setItem('token', token) // Or use HTTP-only cookies
        router.push('/dashboard')
      } else {
        setError('Invalid credentials')
      }
    } catch (err) {
      setError('Login failed')
    }
  }

  return (
    <form onSubmit={handleLogin} className="max-w-md mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Sign In</h1>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded mb-4">
          {error}
        </div>
      )}

      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
        className="w-full px-4 py-2 border rounded mb-4"
      />

      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
        className="w-full px-4 py-2 border rounded mb-4"
      />

      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        Sign In
      </button>
    </form>
  )
}

// lib/api.ts - API Client with JWT
export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('token') // Or get from cookies

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })
}

// Usage
const response = await fetchWithAuth('http://localhost:8000/api/v1/todos')
```

### Backend (FastAPI with JWT Verification)

```python
# core/security.py - JWT Verification
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import Session, select
from models.user import User
from core.database import get_session
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Verify JWT token and return current user.
    Raises 401 if token is invalid or expired.
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Fetch user from database
    user = session.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user

# api/routes/todos.py - Protected Routes
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.todo import Todo, TodoCreate, TodoResponse
from models.user import User
from core.database import get_session
from core.security import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/", response_model=list[TodoResponse])
async def get_todos(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all todos for the authenticated user.
    Filters by user_id from JWT token.
    """
    statement = select(Todo).where(Todo.user_id == current_user.id)
    todos = session.exec(statement).all()
    return todos

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new todo for the authenticated user.
    Automatically sets user_id from JWT token.
    """
    todo = Todo(
        **todo_data.model_dump(),
        user_id=current_user.id  # Set from authenticated user
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific todo.
    Verifies that the todo belongs to the authenticated user.
    """
    todo = session.get(Todo, todo_id)

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Authorization check: ensure todo belongs to current user
    if todo.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this todo"
        )

    return todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a todo.
    Verifies that the todo belongs to the authenticated user.
    """
    todo = session.get(Todo, todo_id)

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(todo)
    session.commit()
    return None

# models/todo.py - Todo Model with User Relationship
from sqlmodel import SQLModel, Field
from typing import Optional

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    completed: bool = False
    user_id: int = Field(foreign_key="user.id")  # Link to user

class TodoCreate(SQLModel):
    title: str
    completed: bool = False

class TodoResponse(SQLModel):
    id: int
    title: str
    completed: bool
    user_id: int
```

## Environment Variables

```bash
# .env (Backend)
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/dbname
JWT_SECRET_KEY=your-secret-key-here-keep-it-secure
ALGORITHM=HS256

# .env.local (Frontend)
NEXT_PUBLIC_API_URL=http://localhost:8000
AUTH_SECRET=your-auth-secret-here
```

## Security Checklist
- [ ] JWT secret stored in environment variables
- [ ] Tokens transmitted over HTTPS only
- [ ] Token expiration implemented and validated
- [ ] Token signature verified on every request
- [ ] User ID extracted from token, not from request body
- [ ] All data queries filtered by authenticated user ID
- [ ] Authorization checks prevent accessing other users' data
- [ ] Invalid/expired tokens return 401 Unauthorized
- [ ] Sensitive data not stored in JWT payload
- [ ] Rate limiting implemented on auth endpoints
