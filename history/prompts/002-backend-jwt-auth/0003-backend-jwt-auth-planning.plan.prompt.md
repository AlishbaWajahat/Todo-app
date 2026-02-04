---
id: 0003
title: backend-jwt-auth-planning
stage: plan
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-backend-jwt-auth
branch: 002-backend-jwt-auth
user: user
command: /sp.plan
labels: ["planning", "architecture", "jwt", "authentication", "api-security"]
links:
  spec: specs/002-backend-jwt-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-backend-jwt-auth/plan.md
  - specs/002-backend-jwt-auth/research.md
  - specs/002-backend-jwt-auth/data-model.md
  - specs/002-backend-jwt-auth/quickstart.md
  - specs/002-backend-jwt-auth/contracts/tasks.yaml
  - CLAUDE.md
tests:
  - Constitution compliance check (all gates passed)
  - Research topics resolution (6 decisions documented)
  - Data model validation (2 entities, relationships, indexes)
  - API contract validation (5 endpoints, OpenAPI spec)
---

## Prompt

/sp.plan

Create:
- Middleware for JWT verification in FastAPI
- Lazy user provisioning logic: ensure every authenticated user has a row in the `users` table
- Updated API endpoints to enforce user identity for task CRUD operations
- Database models for `users` table:
  - id (matches JWT user_id)
  - email
  - name (nullable)
  - avatar_url (nullable)
  - created_at
  - updated_at
- Integration with existing `tasks` table using `user_id` as foreign key

Decisions needing documentation:
- JWT claim used as primary identifier (sub or user_id)
- Error handling strategy for invalid/expired JWTs (HTTP 401)
- Lazy user creation vs pre-populated user table
- Database transaction strategy for user creation on first request
- Middleware placement and request flow order

Implementation approach:
- Incremental build:
  1. Implement JWT middleware
  2. Decode and verify JWT
  3. Extract user_id/email
  4. Check if user exists in `users` table
     - If not → create user row (lazy provisioning)
  5. Enforce user_id filtering for all task endpoints
- Keep all endpoints stateless
- Backend should remain fully compatible with existing frontend (Better Auth JWT)

Testing strategy:
- Manual API tests via FastAPI docs `/docs`
- Validate unauthorized requests return HTTP 401
- Test requests with expired/invalid JWTs
- Test first-time user request → DB row is created
- Test subsequent requests → existing DB row is reused
- Ensure task access is limited to authenticated user only
- Confirm endpoints return correct JSON structure and status codes

Execution phases:
- Foundation: Middleware setup, JWT verification
- User Layer: `users` table creation and lazy provisioning logic
- API Layer: Update endpoints to enforce user ownership
- Validation: End-to-end testing for JWT auth, user creation, and task access
- Cleanup: Remove any temporary/test files, logs, or auto-generated cache

## Response snapshot

Created comprehensive implementation plan for Backend JWT Authentication & API Security:

**Phase 0: Research & Unknowns Resolution**
- Resolved 4 research topics with 6 key decisions documented in research.md
- JWT Verification: Middleware + Dependency hybrid pattern
- User Provisioning: Database constraint + exception handling (idempotent)
- User Isolation: Query filtering with WHERE clauses + database indexes
- JWT Configuration: HS256 algorithm with shared secret
- Error Responses: Structured with detail and code fields
- Logging: Authentication failures only

**Phase 1: Design & Contracts**
- Data Model: 2 entities (User, Task) with relationships and indexes in data-model.md
- API Contracts: 5 authenticated endpoints in OpenAPI format (contracts/tasks.yaml)
- Quickstart Guide: Complete setup and testing instructions in quickstart.md
- Agent Context: Updated CLAUDE.md with new technologies

**Constitution Compliance**
- All security gates passed (JWT authentication, user isolation, secrets management)
- All technology stack requirements satisfied (FastAPI, SQLModel, python-jose, Neon PostgreSQL)
- All API contract requirements met (RESTful, structured errors, OpenAPI docs)
- Spec-driven development workflow followed

**Implementation Strategy**
- 4-phase agent coordination: Database Agent → Auth Agent → Backend Agent → Manual Testing
- Critical path defined with 2-3 day timeline
- 4 risk mitigation strategies documented
- 4 ADR candidates identified for architectural decisions

## Outcome

- ✅ Impact: Complete architectural plan with research, data model, API contracts, and implementation strategy
- 🧪 Tests: Constitution compliance (all gates passed), data model validation, API contract validation
- 📁 Files: plan.md (350+ lines), research.md (200+ lines), data-model.md (400+ lines), quickstart.md (400+ lines), contracts/tasks.yaml (300+ lines)
- 🔁 Next prompts: /sp.tasks (task breakdown), /sp.implement (execution)
- 🧠 Reflection: Planning phase successfully completed all required artifacts. Research resolved all technical unknowns with clear decisions. Data model provides secure multi-user foundation with proper indexes. API contracts define complete authentication flow. Ready for task breakdown and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - all planning phases completed successfully
- Graders run and results (PASS/FAIL): Constitution check PASSED (all gates), Research PASSED (all topics resolved), Design PASSED (complete data model and contracts)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 (research) and Phase 1 (design)
- Next experiment (smallest change to try): Proceed to /sp.tasks for atomic task breakdown
