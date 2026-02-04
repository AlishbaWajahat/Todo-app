<!--
Sync Impact Report - Constitution v1.1.0
========================================
Version Change: 1.0.0 → 1.1.0
Rationale: MINOR version bump - Added testable compliance checks, definition of done, and enhanced principle clarity

Modified Principles:
- Principle I (Spec-Driven Development): Added verification checks
- Principle II (Zero Manual Coding): Added emergency hotfix criteria and verification checks
- Principle V (API Contract Discipline): Added concrete definitions for "consistent", "meaningful errors", and "business logic boundary"

Added Sections:
- Testable Compliance Checks (comprehensive verification criteria)
  - Security Verification (authentication, authorization, secrets)
  - API Contract Verification (RESTful conventions, response format, HTTP status codes)
  - Data Persistence Verification (user isolation, database schema)
  - Frontend-Backend Integration (API communication, business logic boundary)
  - Technology Stack Verification (automated checks)
- Definition of Done (hackathon MVP criteria and out-of-scope items)

Removed Sections: None

Templates Requiring Updates:
- ✅ .specify/templates/plan-template.md (constitution check section compatible)
- ✅ .specify/templates/spec-template.md (acceptance criteria align with testable checks)
- ✅ .specify/templates/tasks-template.md (task verification aligns with compliance checks)
- ✅ .specify/templates/commands/*.md (no updates needed)

Follow-up TODOs: None

Key Improvements:
1. All vague rules converted to testable checks with PASS/FAIL criteria
2. Added concrete definitions for ambiguous terms ("consistent", "meaningful", "business logic")
3. Added clear success criteria (Definition of Done) for hackathon MVP
4. Added emergency hotfix criteria for Zero Manual Coding principle
5. Added automated verification commands for technology stack compliance
-->

# Full-Stack Multi-User Todo Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All development MUST follow the explicit workflow: spec → plan → tasks → implementation.

**Testable Requirements:**
- Every feature begins with a written specification in `specs/<feature>/spec.md`
- Specifications MUST be approved before planning begins
- Plans MUST be derived from approved specs and documented in `specs/<feature>/plan.md`
- Tasks MUST be broken down from approved plans in `specs/<feature>/tasks.md`
- Implementation MUST follow the task list without deviation
- No code may be written without a corresponding spec, plan, and task

**Verification Checks:**
- ✅ PASS: For every code file, a corresponding task exists in `tasks.md`
- ✅ PASS: For every task, a corresponding plan section exists in `plan.md`
- ✅ PASS: For every plan, a corresponding spec exists in `spec.md`
- ✅ PASS: Git commits reference task IDs (e.g., "feat: implement task #3")
- ✅ PASS: PHR (Prompt History Record) exists for each implementation session
- ❌ FAIL: Code exists without traceable spec/plan/task lineage

**Rationale**: Deterministic, reproducible development requires explicit documentation
at every stage. This prevents scope creep, ensures traceability, and enables
AI-assisted development with clear context.

### II. Zero Manual Coding

All code MUST be generated via Claude Code using Spec-Kit Plus tooling.

**Testable Requirements:**
- No manual code writing is permitted
- All implementations MUST use Claude Code agents and skills
- Code generation MUST follow agent-specific guidelines (Frontend, Backend, Database, Auth)
- Manual edits are only permitted for emergency hotfixes (must be documented in ADR)
- All code changes MUST be traceable to a spec/plan/task

**Emergency Hotfix Criteria (Manual Edits Allowed):**
Manual edits are ONLY permitted when ALL of the following are true:
1. Production system is down or critically broken
2. Immediate fix required (cannot wait for spec-driven process)
3. Fix is < 10 lines of code
4. ADR documenting the hotfix is created within 24 hours
5. Proper spec/plan/task created retroactively within 48 hours

**Verification Checks:**
- ✅ PASS: All git commits authored by Claude Code or reference PHR
- ✅ PASS: All code changes have corresponding PHR in `history/prompts/`
- ✅ PASS: Manual edits (if any) have corresponding ADR in `history/adr/`
- ❌ FAIL: Git commits without PHR or ADR documentation

**Rationale**: Ensures consistency, leverages AI capabilities fully, and maintains
a clear audit trail of all development decisions and implementations.

### III. Security-First Architecture (NON-NEGOTIABLE)

Security MUST be the primary consideration in all architectural decisions.

- All API routes MUST require valid JWT authentication
- JWT tokens MUST be verified on every backend request
- User data MUST be strictly isolated (users can only access their own data)
- Database queries MUST filter by authenticated user ID
- No hardcoded secrets or credentials anywhere in codebase
- All secrets MUST be managed via environment variables
- HTTPS MUST be enforced in production
- Authentication failures MUST return 401 Unauthorized
- Authorization failures MUST return 403 Forbidden

**Rationale**: Multi-user applications require strict security boundaries. JWT-based
authentication with proper verification ensures user data isolation and prevents
unauthorized access.

### IV. Technology Stack Adherence

All implementations MUST use the specified technology stack without deviation.

**Frontend:**
- Next.js 16+ with App Router (no Pages Router)
- Tailwind CSS for styling (no other CSS frameworks)
- TypeScript for type safety

**Backend:**
- Python FastAPI (no other Python frameworks)
- SQLModel for ORM (combines SQLAlchemy + Pydantic)
- Pydantic for request/response validation

**Database:**
- Neon Serverless PostgreSQL (no other databases)
- Connection pooling configured for serverless
- Alembic for migrations

**Authentication:**
- Better Auth for frontend authentication
- JWT tokens for backend verification
- python-jose for JWT handling in FastAPI

**Tooling:**
- Claude Code for all code generation
- Spec-Kit Plus for spec-driven workflow

**Rationale**: Technology constraints ensure consistency, enable agent specialization,
and prevent architectural drift. The chosen stack is optimized for serverless
deployment and AI-assisted development.

### V. API Contract Discipline

Frontend and backend MUST communicate exclusively via well-defined REST APIs.

**Testable Requirements:**
- All API endpoints MUST follow RESTful conventions
- Request/response schemas MUST be defined with Pydantic/SQLModel
- API behavior MUST be consistent and predictable
- No direct database access from frontend
- No business logic in frontend (only presentation logic)
- API responses MUST use standard HTTP status codes
- Error responses MUST include meaningful error messages
- API documentation MUST be auto-generated (FastAPI OpenAPI)

**API Consistency Definition:**
"Consistent and predictable" means:
1. Same endpoint always returns same structure for same input
2. Field names use consistent casing (snake_case for API, camelCase for frontend)
3. Timestamps always in ISO 8601 format (e.g., "2026-02-03T10:30:00Z")
4. IDs always integers (not strings or UUIDs)
5. Pagination uses consistent query params: `?skip=0&limit=10`
6. Filtering uses consistent query params: `?completed=true`

**Meaningful Error Messages Definition:**
Error responses MUST include:
1. `detail`: Human-readable error description
2. `code`: Machine-readable error code (e.g., "INVALID_TOKEN", "TODO_NOT_FOUND")
3. `field`: (For validation errors) Which field caused the error
4. NO stack traces or internal error details

Example:
```json
{
  "detail": "Todo not found or you don't have permission to access it",
  "code": "TODO_NOT_FOUND"
}
```

**Business Logic Boundary Definition:**
- ✅ Frontend CAN: Render UI, handle forms, route navigation, display data
- ✅ Frontend CAN: Client-side validation (for UX, not security)
- ❌ Frontend CANNOT: Calculate derived values (e.g., total count, completion percentage)
- ❌ Frontend CANNOT: Filter/sort data (must request filtered data from API)
- ❌ Frontend CANNOT: Enforce business rules (e.g., "max 100 todos per user")

**Verification Checks:**
- ✅ PASS: FastAPI OpenAPI docs accessible at `/docs`
- ✅ PASS: All endpoints return JSON (Content-Type: application/json)
- ✅ PASS: All error responses include `detail` and `code` fields
- ✅ PASS: Frontend code contains no database imports or SQL
- ✅ PASS: Frontend code contains no business logic (only API calls and rendering)
- ❌ FAIL: Frontend calculates values that should come from API

**Rationale**: Clear separation of concerns enables independent development of
frontend and backend, facilitates testing, and ensures maintainability.

### VI. Secrets Management

All sensitive configuration MUST be managed via environment variables.

- No secrets, tokens, or credentials in source code
- No secrets in version control (use .env files, add to .gitignore)
- Environment variables MUST be documented in .env.example
- Production secrets MUST be managed via secure deployment platform
- Database connection strings MUST use environment variables
- JWT secrets MUST be stored in environment variables
- API keys MUST never be hardcoded

**Rationale**: Hardcoded secrets are a critical security vulnerability. Environment-based
configuration enables secure deployment across different environments and prevents
accidental exposure of credentials.

## Testable Compliance Checks

### Security Verification (NON-NEGOTIABLE)

**Authentication Tests:**
- ✅ PASS: API returns 401 when Authorization header is missing
- ✅ PASS: API returns 401 when JWT token is malformed or expired
- ✅ PASS: API returns 401 when JWT signature is invalid
- ✅ PASS: Valid JWT allows access to protected endpoints
- ❌ FAIL: Any endpoint accepts requests without JWT (except public routes)

**Authorization Tests:**
- ✅ PASS: User A cannot access User B's todos (returns 403 or 404)
- ✅ PASS: Database queries include `WHERE user_id = <authenticated_user_id>`
- ✅ PASS: All SQLModel queries filter by authenticated user
- ❌ FAIL: Any query returns data from multiple users without explicit admin role

**Secrets Management Tests:**
- ✅ PASS: `git grep -i "password\|secret\|key" *.py *.ts *.tsx` returns no hardcoded values
- ✅ PASS: `.env.example` exists and documents all required environment variables
- ✅ PASS: `.env` is in `.gitignore`
- ✅ PASS: All secrets loaded from `os.getenv()` or `process.env`
- ❌ FAIL: Any hardcoded connection string, API key, or JWT secret found

### API Contract Verification

**RESTful Conventions:**
- ✅ PASS: GET requests are idempotent (no side effects)
- ✅ PASS: POST creates resources, returns 201 with Location header
- ✅ PASS: PUT/PATCH updates resources, returns 200 or 204
- ✅ PASS: DELETE removes resources, returns 204
- ✅ PASS: All endpoints follow `/api/v1/<resource>` pattern

**Response Format Consistency:**
- ✅ PASS: Success responses return JSON with consistent schema
- ✅ PASS: Error responses follow format: `{"detail": "Error message", "code": "ERROR_CODE"}`
- ✅ PASS: All timestamps in ISO 8601 format
- ✅ PASS: All IDs are integers (not UUIDs or strings)
- ❌ FAIL: Inconsistent response structures across endpoints

**HTTP Status Codes:**
- ✅ PASS: 200 for successful GET/PUT/PATCH
- ✅ PASS: 201 for successful POST (resource created)
- ✅ PASS: 204 for successful DELETE (no content)
- ✅ PASS: 400 for validation errors (with field-level details)
- ✅ PASS: 401 for authentication failures
- ✅ PASS: 403 for authorization failures
- ✅ PASS: 404 for resource not found
- ✅ PASS: 500 for server errors (with generic message, no stack traces)

### Data Persistence Verification

**User Isolation:**
- ✅ PASS: Each todo has `user_id` foreign key to `user.id`
- ✅ PASS: All queries filter by authenticated user's ID
- ✅ PASS: User A's data never appears in User B's responses
- ❌ FAIL: Any cross-user data leakage detected

**Database Schema:**
- ✅ PASS: All tables have primary keys
- ✅ PASS: Foreign keys defined with proper constraints
- ✅ PASS: Indexes exist on `user_id` columns
- ✅ PASS: Migrations are reversible (up/down)
- ✅ PASS: No raw SQL strings (use SQLModel/Alembic)

### Frontend-Backend Integration

**API Communication:**
- ✅ PASS: Frontend includes JWT in `Authorization: Bearer <token>` header
- ✅ PASS: Frontend handles 401 by redirecting to login
- ✅ PASS: Frontend handles 403 with appropriate error message
- ✅ PASS: Frontend displays validation errors from 400 responses
- ❌ FAIL: Frontend makes direct database calls

**Business Logic Boundary:**
- ✅ PASS: Frontend only contains presentation logic (rendering, form handling, routing)
- ✅ PASS: All data validation happens in backend (Pydantic models)
- ✅ PASS: All data transformations happen in backend
- ❌ FAIL: Frontend contains business rules (e.g., calculating totals, filtering by status)

### Technology Stack Verification

**Automated Checks:**
```bash
# Frontend stack verification
✅ PASS: package.json includes "next": "^16.0.0"
✅ PASS: package.json includes "tailwindcss"
✅ PASS: All .tsx files use TypeScript
✅ PASS: app/ directory exists (App Router)
❌ FAIL: pages/ directory exists (Pages Router prohibited)

# Backend stack verification
✅ PASS: requirements.txt includes "fastapi"
✅ PASS: requirements.txt includes "sqlmodel"
✅ PASS: requirements.txt includes "python-jose"
✅ PASS: All .py files use FastAPI decorators
❌ FAIL: Flask, Django, or other frameworks detected

# Database verification
✅ PASS: DATABASE_URL contains "neon.tech"
✅ PASS: Alembic migrations directory exists
✅ PASS: SQLModel models use table=True
❌ FAIL: MongoDB, MySQL, or SQLite imports detected
```

## Definition of Done

### Hackathon MVP Criteria

The project is considered **DONE** when all of the following are met:

**Functional Requirements:**
1. ✅ User can sign up with email/password (Better Auth)
2. ✅ User can sign in and receive JWT token
3. ✅ User can create a new todo item
4. ✅ User can view their own todo list (filtered by user_id)
5. ✅ User can mark todo as complete/incomplete
6. ✅ User can delete their own todo
7. ✅ User cannot see or modify other users' todos

**Technical Requirements:**
1. ✅ All API endpoints require valid JWT (except signup/signin)
2. ✅ All database queries filter by authenticated user ID
3. ✅ Frontend built with Next.js App Router + Tailwind CSS
4. ✅ Backend built with FastAPI + SQLModel
5. ✅ Database is Neon Serverless PostgreSQL
6. ✅ No hardcoded secrets (all in environment variables)
7. ✅ All code generated via Claude Code (traceable to specs/plans/tasks)

**Documentation Requirements:**
1. ✅ Feature spec exists in `specs/<feature>/spec.md`
2. ✅ Implementation plan exists in `specs/<feature>/plan.md`
3. ✅ Task list exists in `specs/<feature>/tasks.md`
4. ✅ `.env.example` documents all required environment variables
5. ✅ README.md includes setup instructions

**Security Requirements:**
1. ✅ All security verification tests pass (see Testable Compliance Checks)
2. ✅ Auth Agent has audited authentication implementation
3. ✅ No secrets in git history (`git log -p | grep -i "password\|secret"` returns nothing)

**Deployment Readiness:**
1. ✅ Frontend runs on `localhost:3000` (or deployed URL)
2. ✅ Backend runs on `localhost:8000` (or deployed URL)
3. ✅ Database migrations applied successfully
4. ✅ CORS configured for frontend-backend communication

### Out of Scope (Explicitly NOT Required)

- ❌ User profile editing
- ❌ Password reset functionality
- ❌ Email verification
- ❌ Todo categories or tags
- ❌ Todo due dates or priorities
- ❌ Sharing todos with other users
- ❌ Real-time updates (WebSockets)
- ❌ Mobile app
- ❌ Automated tests (unit/integration)
- ❌ CI/CD pipeline
- ❌ Production deployment

## Technology Stack Requirements

### Mandatory Technologies

**Frontend Stack:**
- Framework: Next.js 16+ (App Router only)
- Styling: Tailwind CSS
- Language: TypeScript
- State Management: React hooks (useState, useContext)
- Data Fetching: Server Components with async/await

**Backend Stack:**
- Framework: Python FastAPI
- ORM: SQLModel
- Validation: Pydantic (included in SQLModel)
- Authentication: python-jose for JWT
- Server: Uvicorn (ASGI server)

**Database Stack:**
- Database: Neon Serverless PostgreSQL
- Connection Pooling: PgBouncer (recommended)
- Migrations: Alembic
- Query Builder: SQLModel select()

**Authentication Stack:**
- Frontend: Better Auth
- Backend: JWT token verification
- Token Format: JSON Web Tokens (JWT)
- Algorithm: HS256 (HMAC with SHA-256)

### Prohibited Technologies

- No other frontend frameworks (React without Next.js, Vue, Angular, etc.)
- No other CSS frameworks (Bootstrap, Material-UI, etc.)
- No other backend frameworks (Django, Flask, Express, etc.)
- No other ORMs (raw SQLAlchemy, Prisma, TypeORM, etc.)
- No other databases (MongoDB, MySQL, SQLite, etc.)
- No session-based authentication (only JWT)

## Development Workflow

### Spec-Driven Process

1. **Specification Phase** (`/sp.specify`)
   - Write feature specification in `specs/<feature>/spec.md`
   - Define requirements, acceptance criteria, and constraints
   - Get user approval before proceeding

2. **Planning Phase** (`/sp.plan`)
   - Create architectural plan in `specs/<feature>/plan.md`
   - Define API contracts, data models, and component structure
   - Identify architectural decisions requiring ADRs
   - Get user approval before proceeding

3. **Task Breakdown Phase** (`/sp.tasks`)
   - Generate task list in `specs/<feature>/tasks.md`
   - Break plan into atomic, testable tasks
   - Define acceptance criteria for each task
   - Order tasks by dependencies

4. **Implementation Phase** (`/sp.implement`)
   - Execute tasks sequentially using appropriate agents
   - Use Frontend Agent for Next.js components
   - Use Backend Agent for FastAPI endpoints
   - Use Database Agent for schema and migrations
   - Use Auth Agent for authentication/authorization
   - Create PHR (Prompt History Record) for each significant interaction

5. **Verification Phase**
   - Run tests for each completed task
   - Verify acceptance criteria met
   - Ensure security requirements satisfied
   - Check constitution compliance

### Agent Usage

**Frontend Agent** (`frontend-agent`):
- Use for: Next.js pages, components, layouts, Tailwind styling
- Required Skill: Frontend Skill
- Responsibilities: UI/UX, client-side logic, API integration

**Backend Agent** (`fastapi-backend-agent`):
- Use for: FastAPI routes, request/response models, business logic
- Required Skill: Backend Skill
- Responsibilities: API endpoints, validation, error handling

**Database Agent** (`database-agent`):
- Use for: Schema design, migrations, query optimization
- Required Skill: Database Skill
- Responsibilities: Data modeling, database operations, indexing

**Auth Agent** (`auth-security-auditor`):
- Use for: Authentication flows, JWT verification, security audits
- Required Skill: Auth Skill
- Responsibilities: Security implementation, token handling, authorization

### Multi-Agent Coordination

For features spanning multiple layers, coordinate agents in this order:
1. **Database Agent** → Design schema and tables
2. **Backend Agent** → Create API endpoints with database integration
3. **Auth Agent** → Add authentication/authorization to endpoints
4. **Frontend Agent** → Build UI that consumes the APIs

## Governance

### Constitution Authority

This constitution supersedes all other development practices, guidelines, or
conventions. In case of conflict, constitution principles take precedence.

### Compliance Requirements

- All pull requests MUST verify constitution compliance
- All code reviews MUST check adherence to core principles
- All architectural decisions MUST align with technology stack requirements
- All security implementations MUST follow security-first architecture
- Violations MUST be documented and remediated immediately

### Amendment Process

1. Propose amendment with clear rationale
2. Document impact on existing code and processes
3. Update dependent templates and documentation
4. Increment version according to semantic versioning:
   - MAJOR: Backward-incompatible principle changes
   - MINOR: New principles or sections added
   - PATCH: Clarifications, wording improvements
5. Create ADR for significant governance changes
6. Update this file with sync impact report

### Version Control

All constitution changes MUST be version controlled with:
- Clear commit messages describing changes
- Sync impact report at top of file
- Updated version number and amendment date
- PHR documenting the amendment process

### Enforcement

- Automated checks SHOULD verify technology stack adherence
- Code generation MUST use specified agents and skills
- Security audits MUST be performed for authentication code
- Constitution violations MUST be treated as critical issues

**Version**: 1.1.0 | **Ratified**: 2026-02-03 | **Last Amended**: 2026-02-03
