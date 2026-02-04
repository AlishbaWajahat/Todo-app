# Research: JWT Authentication & User Provisioning

**Feature**: Backend JWT Authentication & API Security
**Date**: 2026-02-05
**Purpose**: Resolve technical unknowns and establish implementation patterns

## 1. JWT Verification Best Practices in FastAPI

### Decision: Middleware + Dependency Injection Hybrid

**Rationale**:
- **Middleware** for global JWT validation and user provisioning (runs on every request)
- **Dependency** for accessing current user in route handlers (type-safe, testable)

**Pattern**:
```python
# Middleware: Validates JWT, provisions user, stores in request.state
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Extract and validate JWT
    # Provision user if needed
    # Store user in request.state.user
    return await call_next(request)

# Dependency: Retrieves user from request.state
def get_current_user(request: Request) -> User:
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Authentication required")
    return request.state.user

# Route: Uses dependency for type-safe access
@app.get("/tasks")
def get_tasks(current_user: User = Depends(get_current_user)):
    # current_user is guaranteed to exist and be valid
    pass
```

**Alternatives Considered**:
- **Dependency-only**: Would require repeating JWT validation logic on every route (inefficient)
- **Middleware-only**: Would require accessing request.state directly in routes (not type-safe)

**Performance**: Middleware adds ~5-10ms overhead per request (JWT signature verification). Dependency adds <1ms (simple attribute access).

**Error Handling**:
- Middleware catches JWT validation errors and returns 401 with structured error response
- Dependency raises HTTPException if user not found in request.state
- All authentication failures logged for security monitoring

## 2. Lazy User Provisioning Patterns

### Decision: Database-Level Unique Constraint + Exception Handling

**Rationale**:
- PostgreSQL UNIQUE constraint on user.id prevents duplicate user records at database level
- Python exception handling for IntegrityError provides idempotent user creation
- No application-level locking required (database handles concurrency)

**Pattern**:
```python
from sqlalchemy.exc import IntegrityError

async def provision_user(user_id: str, email: str, name: str) -> User:
    # Attempt to create user
    try:
        user = User(id=user_id, email=email, name=name)
        session.add(user)
        await session.commit()
        return user
    except IntegrityError:
        # User already exists (race condition), fetch existing
        await session.rollback()
        user = await session.get(User, user_id)
        return user
```

**Alternatives Considered**:
- **SELECT then INSERT**: Vulnerable to race conditions (two requests could both see no user and both insert)
- **Pessimistic locking**: Requires SELECT FOR UPDATE, adds complexity and reduces concurrency
- **Optimistic locking**: Requires version columns, unnecessary for simple user provisioning

**Race Condition Handling**:
- Request 1 and Request 2 arrive simultaneously for new user
- Both attempt INSERT
- One succeeds, one fails with IntegrityError
- Failed request rolls back and fetches existing user
- Both requests proceed with same user record

**Database Transaction Strategy**:
- User provisioning uses implicit transaction (session.commit())
- Task operations use separate transactions (not mixed with user provisioning)
- Rollback on IntegrityError ensures clean state

## 3. SQLModel User Isolation Patterns

### Decision: Query Filtering with WHERE Clauses + Database Indexes

**Rationale**:
- Every task query includes `WHERE user_id = <authenticated_user_id>`
- Database index on tasks.user_id ensures fast filtering (O(log n) lookup)
- SQLModel select() provides type-safe query building

**Pattern**:
```python
from sqlmodel import select

# Get all tasks for authenticated user
def get_user_tasks(session: Session, user_id: str) -> list[Task]:
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks

# Get specific task for authenticated user (returns None if not found or wrong user)
def get_user_task(session: Session, task_id: int, user_id: str) -> Task | None:
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    return task
```

**Performance Optimization**:
- Index on `tasks.user_id` column (created in migration)
- Index on `(tasks.id, tasks.user_id)` for single-task lookups (composite index)
- Query execution time: <10ms for typical user task lists (<1000 tasks)

**Preventing N+1 Queries**:
- Not applicable for this feature (no relationships loaded)
- Future optimization: Use `selectinload()` if loading user.tasks relationship

**Security Guarantee**:
- User A cannot access User B's tasks (query returns empty result)
- Returns 404 Not Found (not 403 Forbidden) to prevent information leakage
- No way to bypass user_id filter (enforced at query level, not application level)

## 4. python-jose JWT Configuration

### Decision: HS256 Algorithm with Shared Secret

**Rationale**:
- HS256 (HMAC with SHA-256) is symmetric algorithm (same secret for signing and verification)
- Better Auth uses HS256 by default for JWT signing
- Shared secret (JWT_SECRET) must be identical between Better Auth and FastAPI backend
- Simpler than RS256 (no public/private key pair management)

**Configuration**:
```python
from jose import jwt, JWTError

JWT_SECRET = os.getenv("JWT_SECRET")  # Must match Better Auth secret
JWT_ALGORITHM = "HS256"

def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,  # Verify expiration
                "verify_iat": True,  # Verify issued-at
            }
        )
        return payload
    except JWTError as e:
        # Token invalid, expired, or signature mismatch
        raise HTTPException(status_code=401, detail="Invalid or expired token")
```

**Token Expiration Validation**:
- python-jose automatically validates `exp` claim (expiration timestamp)
- Expired tokens raise `ExpiredSignatureError` (subclass of JWTError)
- No manual timestamp comparison needed

**Custom Claims Extraction**:
- `sub` claim: User ID (required, used as primary key in users table)
- `email` claim: User email (optional, stored in users table)
- `name` claim: User display name (optional, stored in users table)
- `exp` claim: Expiration timestamp (validated automatically)
- `iat` claim: Issued-at timestamp (validated automatically)

**Alternatives Considered**:
- **RS256**: Requires public/private key pair, more complex setup, unnecessary for single backend
- **ES256**: Requires elliptic curve keys, not supported by Better Auth by default

**Security Considerations**:
- JWT_SECRET must be strong (minimum 32 characters, random)
- JWT_SECRET must be kept secret (never committed to git)
- JWT_SECRET must match between Better Auth and FastAPI backend
- Token expiration should be reasonable (1-24 hours recommended)

## 5. Error Response Standardization

### Decision: Structured Error Responses with Detail and Code

**Pattern**:
```python
from fastapi import HTTPException

# Authentication failure
raise HTTPException(
    status_code=401,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"}
)

# Authorization failure (task not found or wrong user)
raise HTTPException(
    status_code=404,
    detail="Task not found or you don't have permission to access it"
)

# Validation error (handled automatically by FastAPI/Pydantic)
# Returns 422 with field-level error details
```

**Logging Strategy**:
- Log all authentication failures (401 responses) with timestamp, IP, and error reason
- Do NOT log successful authentications (too noisy, performance impact)
- Log user provisioning events (new user created)
- Use Python logging module with structured format

**Example Log Entry**:
```
2026-02-05 10:30:45 [ERROR] Authentication failed: Invalid token signature (IP: 192.168.1.100)
2026-02-05 10:31:12 [INFO] User provisioned: user_id=abc123, email=user@example.com
```

## Summary of Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| JWT Verification | Middleware + Dependency hybrid | Global validation + type-safe route access |
| User Provisioning | Database constraint + exception handling | Idempotent, handles race conditions |
| User Isolation | Query filtering with indexes | Fast, secure, prevents cross-user access |
| JWT Algorithm | HS256 with shared secret | Simple, compatible with Better Auth |
| Error Responses | Structured with detail and code | Consistent, debuggable, secure |
| Logging | Failures only | Security monitoring without noise |

## Implementation Readiness

All research topics resolved. No blocking unknowns remain. Ready to proceed to Phase 1 (Design & Contracts).
