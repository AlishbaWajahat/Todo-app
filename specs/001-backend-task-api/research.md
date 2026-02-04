# Research & Technical Decisions

**Feature**: Backend Core – Task API & Database Layer
**Date**: 2026-02-03
**Phase**: Phase 0 - Research

## Overview

This document captures all technical research and decisions made during the planning phase. Each decision includes the chosen approach, rationale, and alternatives considered.

---

## Decision 1: Database Schema Design

**Question**: How should we structure the Task entity's primary key and user_id field?

**Decision**: Use integer primary key for task.id and integer for user_id

**Rationale**:
- Integer PKs are simpler and more performant than UUIDs for hackathon scale
- Better join performance when adding user table in future phase
- Sufficient uniqueness for expected scale (<1000 users, <100k tasks)
- Standard PostgreSQL SERIAL type provides auto-increment
- Compatible with SQLModel's default Field(default=None, primary_key=True) pattern

**Alternatives Considered**:
1. **UUIDs**: More scalable for distributed systems, but overkill for MVP. Adds complexity and storage overhead.
2. **String IDs**: Less efficient for indexing and joins. No clear benefit over integers.
3. **Composite keys**: Unnecessary complexity for single-table design.

**Implementation Impact**: Use `id: Optional[int] = Field(default=None, primary_key=True)` in SQLModel

---

## Decision 2: SQLModel vs Raw SQL

**Question**: Should we use SQLModel ORM or write raw SQL queries?

**Decision**: Use SQLModel exclusively (no raw SQL)

**Rationale**:
- Type safety: SQLModel combines SQLAlchemy ORM with Pydantic validation
- Reduced boilerplate: Single model definition for database and API schemas
- Automatic validation: Pydantic validates data before database operations
- Better maintainability: Changes to schema automatically propagate
- FastAPI integration: SQLModel models work seamlessly with FastAPI responses
- Constitution compliance: Aligns with "Technology Stack Adherence" principle

**Alternatives Considered**:
1. **Raw SQL**: More control and potentially better performance, but verbose and error-prone. Loses type safety.
2. **SQLAlchemy Core**: Middle ground between ORM and raw SQL. More complex than SQLModel without clear benefits.
3. **Async SQLAlchemy**: Better for high concurrency, but adds complexity. Not needed for hackathon MVP scale.

**Implementation Impact**: All database operations use SQLModel Session and select() queries

---

## Decision 3: user_id Representation

**Question**: How should user_id be stored and validated?

**Decision**: Integer type, required field, no foreign key constraint yet

**Rationale**:
- Simple integer type matches future user.id primary key
- Required field ensures every task has an owner
- No foreign key constraint because user table doesn't exist in this phase
- Compatible with future auth integration (JWT will contain user_id as integer)
- Pydantic validation ensures positive integer values

**Alternatives Considered**:
1. **UUID**: Overkill for MVP, adds complexity. No clear benefit.
2. **String**: Less efficient for indexing. Would require conversion when adding user table.
3. **Foreign key now**: Requires creating user table in this phase, which is out of scope.
4. **Optional user_id**: Violates future auth requirements. Every task must belong to a user.

**Implementation Impact**: `user_id: int = Field(...)` with Pydantic validation for positive integers

---

## Decision 4: Error Handling Strategy

**Question**: How should we structure error responses and HTTP status codes?

**Decision**: Use FastAPI HTTPException with detail and custom error codes

**Rationale**:
- Standard FastAPI pattern for raising HTTP errors
- Consistent error format: `{"detail": "message", "code": "ERROR_CODE"}`
- Automatic OpenAPI documentation of error responses
- Easy to extend with custom exception handlers
- Aligns with constitution's "API Contract Discipline" principle

**Error Response Format**:
```json
{
  "detail": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE"
}
```

**Status Code Mapping**:
- 200: Successful GET/PUT/PATCH
- 201: Successful POST (resource created)
- 204: Successful DELETE (no content)
- 400: Validation error (missing/invalid fields)
- 404: Resource not found
- 500: Server error (database connection failure, etc.)

**Alternatives Considered**:
1. **Custom exception classes**: More flexible but adds complexity. Not needed for MVP.
2. **Plain HTTP responses**: Less structured, harder to maintain consistency.
3. **Problem Details (RFC 7807)**: More formal but overkill for hackathon MVP.

**Implementation Impact**: Raise `HTTPException(status_code=404, detail="Task not found")` in endpoints

---

## Decision 5: Environment Variable Management

**Question**: How should we load and validate environment variables?

**Decision**: Use python-dotenv to load .env file, Pydantic Settings for validation

**Rationale**:
- python-dotenv: Standard Python library for loading .env files
- Pydantic Settings: Type-safe configuration with automatic validation
- Fail-fast: Application won't start if required variables are missing
- Easy testing: Can override settings in tests
- Constitution compliance: "Secrets Management" principle requires environment variables

**Configuration Structure**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
```

**Alternatives Considered**:
1. **os.getenv() directly**: No validation, easy to miss required variables.
2. **Config files (YAML/JSON)**: Less secure for secrets, harder to deploy.
3. **Environment-only (no .env)**: Harder for local development.

**Implementation Impact**: Create core/config.py with Pydantic Settings class

---

## Decision 6: Connection Pooling for Neon

**Question**: How should we configure database connection pooling for Neon's serverless architecture?

**Decision**: Use SQLModel's default connection pooling with pool_pre_ping=True

**Rationale**:
- pool_pre_ping=True: Verifies connections before use, handles serverless cold starts
- Default pool_size (5) and max_overflow (10): Sufficient for hackathon MVP
- No external dependencies: Uses SQLAlchemy's built-in pooling
- Neon-compatible: Works well with Neon's connection limits

**Connection Configuration**:
```python
engine = create_engine(
    database_url,
    echo=True,  # Log SQL queries in development
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,
    max_overflow=10
)
```

**Alternatives Considered**:
1. **PgBouncer**: External connection pooler. Adds deployment complexity, not needed for MVP.
2. **Custom pooling**: Unnecessary complexity, SQLAlchemy's pooling is battle-tested.
3. **No pooling**: Poor performance, creates new connection for every request.

**Implementation Impact**: Configure engine in core/database.py with pool_pre_ping=True

---

## Decision 7: Timestamp Handling

**Question**: How should we handle created_at and updated_at timestamps?

**Decision**: Use datetime.utcnow() for timestamps, store as TIMESTAMP in PostgreSQL

**Rationale**:
- UTC timestamps: Avoids timezone confusion, standard practice
- datetime.utcnow(): Python standard library, no external dependencies
- TIMESTAMP type: PostgreSQL native type, efficient storage
- ISO 8601 format: FastAPI automatically serializes to ISO 8601 in JSON responses
- Auto-update: Use SQLModel's default_factory for created_at, update manually for updated_at

**Model Definition**:
```python
from datetime import datetime

created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Alternatives Considered**:
1. **Unix timestamps**: Less readable, harder to debug. No clear benefit.
2. **Timezone-aware datetime**: More complex, not needed for MVP. All times in UTC.
3. **Database-generated timestamps**: Requires DEFAULT CURRENT_TIMESTAMP in schema. Less control from application.

**Implementation Impact**: Use datetime.utcnow() in SQLModel Field default_factory

---

## Decision 8: API Versioning

**Question**: Should we version the API, and if so, how?

**Decision**: Use /api/v1 prefix for all endpoints

**Rationale**:
- Future-proof: Enables API v2 without breaking existing clients
- Clear versioning: Version in URL path is discoverable and explicit
- Standard practice: Most REST APIs use URL path versioning
- FastAPI support: Easy to implement with APIRouter prefix

**URL Structure**:
- Base: http://localhost:8000
- API root: /api/v1
- Tasks: /api/v1/tasks
- Specific task: /api/v1/tasks/{task_id}

**Alternatives Considered**:
1. **No versioning**: Harder to evolve API without breaking changes.
2. **Header-based versioning**: Less discoverable, harder to test in browser.
3. **Query parameter versioning**: Non-standard, clutters URLs.

**Implementation Impact**: Use `APIRouter(prefix="/api/v1")` in FastAPI

---

## Technology Stack Summary

### Core Technologies

**FastAPI** (Backend Framework)
- Automatic OpenAPI documentation
- Pydantic validation built-in
- Async support for high performance
- Excellent developer experience
- Type hints throughout

**SQLModel** (ORM)
- Combines SQLAlchemy ORM + Pydantic validation
- Single model definition for database and API
- Type-safe database operations
- Reduces boilerplate code
- Perfect FastAPI integration

**Neon PostgreSQL** (Database)
- Serverless architecture (auto-scaling)
- Instant database branching for development
- Zero-downtime migrations
- Built-in connection pooling
- Generous free tier for hackathons

**Uvicorn** (ASGI Server)
- Production-ready ASGI server
- Supports async operations
- Fast and lightweight
- Standard choice for FastAPI

### Supporting Libraries

- **python-dotenv**: Load environment variables from .env file
- **psycopg2-binary**: PostgreSQL adapter for Python
- **pydantic-settings**: Type-safe configuration management
- **python-jose**: JWT handling (for future auth phase)

---

## Performance Considerations

**Expected Load**: <1000 concurrent users, <100 requests/second

**Performance Targets**:
- p95 latency: <200ms
- Database queries: <50ms
- Connection pool: 5 base + 10 overflow = 15 max connections

**Optimization Strategy**:
- Use connection pooling to avoid connection overhead
- Keep queries simple (no complex joins in this phase)
- Use database indexes on primary keys (automatic)
- Defer pagination and caching to future phases

---

## Security Considerations

**Current Phase** (No Auth Enforcement):
- user_id field exists but not validated against JWT
- All endpoints publicly accessible
- No authorization checks

**Future Phase** (Auth Integration):
- Add JWT verification middleware
- Extract user_id from JWT token
- Filter all queries by authenticated user_id
- Add 401/403 error responses

**Secrets Management**:
- DATABASE_URL in environment variable
- No hardcoded credentials
- .env file in .gitignore
- .env.example documents required variables

---

## Development Workflow

**Local Development**:
1. Clone repository
2. Create .env file from .env.example
3. Add Neon DATABASE_URL
4. Install dependencies: `pip install -r requirements.txt`
5. Run server: `uvicorn main:app --reload`
6. Access docs: http://localhost:8000/docs

**Testing Workflow**:
1. Use FastAPI /docs for manual testing
2. Test each endpoint with valid inputs
3. Test error cases (missing fields, invalid IDs)
4. Verify database persistence (restart server)
5. Check response format consistency

---

## Risks & Mitigations

**Risk**: Database connection failures
**Mitigation**: pool_pre_ping=True, graceful error handling

**Risk**: Invalid user_id values
**Mitigation**: Pydantic validation, database NOT NULL constraint

**Risk**: Missing environment variables
**Mitigation**: Pydantic Settings validation, fail-fast on startup

**Risk**: Neon connection limits
**Mitigation**: Appropriate pool configuration, monitor connection usage
