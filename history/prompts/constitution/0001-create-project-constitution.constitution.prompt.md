---
id: 0001
title: Create project constitution
stage: constitution
date: 2026-02-03
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "governance", "project-setup", "initial-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Project: Full-Stack Multi-User Todo Web Application

Core principles:
- Spec-driven development (spec → plan → tasks → implementation)
- Zero manual coding (all code generated via Claude Code)
- Security-first architecture (JWT-based authentication)
- Clear separation of frontend and backend responsibilities
- Deterministic, reproducible development process

Key standards:
- All features must map directly to written specs
- Every implementation must follow an explicit plan
- Authentication must enforce strict user isolation
- API behavior must be consistent and predictable
- Frontend and backend must communicate only via REST APIs
- Environment-based secrets management (no hardcoded secrets)

Technology constraints:
- Frontend: Next.js 16+ (App Router)
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT
- Spec-driven tooling: Claude Code + Spec-Kit Plus

Security requirements:
- All API routes require a valid JWT
- JWT must be verified on every backend request
- User data must be strictly isolated
- Database queries must filter by authenticated user ID

## Response snapshot

Created initial project constitution (v1.0.0) with 6 core principles:

1. **Spec-Driven Development (NON-NEGOTIABLE)**: Enforces spec → plan → tasks → implementation workflow
2. **Zero Manual Coding**: All code must be generated via Claude Code
3. **Security-First Architecture (NON-NEGOTIABLE)**: JWT authentication with strict user isolation
4. **Technology Stack Adherence**: Mandates Next.js, FastAPI, SQLModel, Neon PostgreSQL, Better Auth
5. **API Contract Discipline**: RESTful APIs with clear frontend/backend separation
6. **Secrets Management**: Environment variables only, no hardcoded credentials

Additional sections:
- Technology Stack Requirements (mandatory and prohibited technologies)
- Development Workflow (spec-driven process with agent coordination)
- Governance (compliance, amendments, enforcement)

Constitution file created at: `.specify/memory/constitution.md`

## Outcome

- ✅ Impact: Project governance established with clear principles and technology constraints
- 🧪 Tests: N/A (constitution is documentation)
- 📁 Files: 1 file created (.specify/memory/constitution.md)
- 🔁 Next prompts: Begin feature development with /sp.specify for first feature
- 🧠 Reflection: Constitution provides clear guardrails for AI-assisted development with explicit technology stack and security requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (initial constitution)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution compliance during first feature implementation
