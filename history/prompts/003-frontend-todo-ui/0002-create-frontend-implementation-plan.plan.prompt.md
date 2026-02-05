---
id: 0002
title: Create Frontend Implementation Plan
stage: plan
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-frontend-todo-ui
branch: 003-frontend-todo-ui
user: Alishba wajahat
command: /sp.plan
labels: ["planning", "frontend", "architecture", "next.js", "better-auth", "jwt", "api-integration"]
links:
  spec: specs/003-frontend-todo-ui/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-frontend-todo-ui/plan.md
 - specs/003-frontend-todo-ui/research.md
 - specs/003-frontend-todo-ui/data-model.md
 - specs/003-frontend-todo-ui/contracts/api-integration.md
 - specs/003-frontend-todo-ui/quickstart.md
 - CLAUDE.md (updated with new technologies)
tests:
 - N/A (planning phase)
---

## Prompt

/sp.plan

Objective:
Transform the existing frontend folder into a fully functional, secure, and modular Todo app UI, preserving the current theme and profile UI while integrating with backend APIs (FastAPI + JWT) from Specs 1 & 2.

Execution Phases:

1. **Foundation Review**
   - Inspect the existing frontend folder structure
   - Document: Current pages, Components, Theme (colors, typography), Profile feature
   - Identify unused files or components for potential cleanup
   - Validate existing Tailwind setup and App Router configuration

2. **Authentication & JWT Integration**
   - Ensure Better Auth JWT flow is functional
   - Verify login, logout, and token persistence across page reloads
   - Modify frontend API client to attach JWT in `Authorization: Bearer <token>` header for all requests
   - Ensure all API calls respect authenticated user and backend restrictions
   - Test unauthorized access → returns correct UI state (e.g., redirect to login)

3. **Todo Feature Implementation**
   - Add/extend pages for: Task list view (read), Task creation form (create), Task editing form (update), Task deletion (delete), Task completion toggle (patch)
   - Ensure responsiveness (mobile + desktop)
   - Integrate with backend endpoints from Specs 1 & 2
   - Maintain modular structure: Components → reusable UI elements, Pages → route-based logic, API client → centralized fetch functions, State → local where possible, minimal global state

4. **Profile Feature Enhancement**
   - Extend profile page: Display current user info (name, avatar), Allow editing and updating of profile data, Persist changes via backend API
   - Reuse existing profile components and theme
   - Validate refresh → data persists

5. **Codebase Cleanup & Modularization**
   - Remove unused components, files, logs, or temporary artifacts
   - Ensure folder structure is logical and modular
   - Verify naming conventions, consistent formatting, and separation of concerns
   - Refactor duplicated logic where necessary
   - Ensure CSS / Tailwind utility classes follow consistent patterns

6. **Validation & Testing**
   - Manual test flows: Sign up, login, logout, CRUD tasks, Task completion toggle, Profile update and persistence
   - Verify responsive UI on multiple screen sizes
   - Ensure all API calls succeed and errors are handled gracefully
   - Check theme consistency across all pages and components
   - Confirm no unused files exist and structure is clean

Decisions needing documentation:
- Folder structure for pages, components, and API client
- State management approach (local vs minimal global)
- Profile component extensions vs new components
- Error handling strategy for API calls
- Any new utility functions or hooks created

Execution Notes:
- Incremental implementation: Foundation → Auth → Tasks → Profile → Cleanup → Validation
- Maintain strict modularization to support future specs
- Keep existing cute shimmery girly theme consistent
- Remove temporary or unused artifacts

## Response snapshot

Created comprehensive implementation plan for frontend Todo app with complete Phase 0 (Research) and Phase 1 (Design & Contracts) deliverables.

**Plan Structure (plan.md - 840 lines)**:
- Technical Context: TypeScript 5.x, Next.js 16 App Router, Better Auth, Tailwind CSS 4
- Constitution Check: All gates passed (Security-First, Tech Stack, API Contract, Spec-Driven, Zero Manual Coding)
- Project Structure: Detailed Next.js App Router structure with route groups (auth, protected)
- Phase 0: Research topics identified (7 technical decisions)
- Phase 1: Data model, API contracts, quickstart guide
- Phase 2: Task breakdown (44-57 estimated tasks across 6 categories)
- Architectural Decisions: 7 key decisions documented with rationale
- Implementation Phases: 4 phases (Foundation & Auth, Task Management, Profile, UI/UX Polish)
- Risk Assessment: High/Medium/Low risks identified with mitigations
- Success Metrics: Functional, performance, quality, and UX metrics

**Research Document (research.md - 400+ lines)**:
1. Better Auth Integration: httpOnly cookies for JWT storage (XSS-safe)
2. API Client Architecture: Centralized fetch wrapper with automatic JWT injection
3. Route Protection: Next.js middleware for server-side authentication
4. State Management: React Server Components with minimal client-side state
5. Form Handling: HTML5 native validation with progressive enhancement
6. Theme Integration: Tailwind CSS extended with existing purple/pink palette
7. Error Handling: Layered approach (global boundary + API client + component-level)

**Data Model (data-model.md - 400+ lines)**:
- Core Entities: User, Task, Session
- API Types: ApiResponse<T>, ApiError
- Form Data Types: TaskCreateData, TaskUpdateData, ProfileFormData, SignUpFormData, SignInFormData
- UI State Types: TaskFilter, TaskSort, LoadingState
- Component Hierarchy: Complete tree structure
- Type Exports: Centralized type definitions
- Validation Utilities: Helper functions

**API Contracts (contracts/api-integration.md - 600+ lines)**:
- Authentication Endpoints: Sign up, Sign in
- Task Endpoints: List, Get, Create, Update, Delete (full CRUD)
- User Profile Endpoints: Get profile, Update profile, Upload avatar
- Error Response Format: Consistent structure with codes
- Frontend Integration Patterns: API client setup and usage examples
- CORS Configuration: Frontend and backend settings
- Testing Examples: cURL commands and FastAPI docs

**Quickstart Guide (quickstart.md - 400+ lines)**:
- Prerequisites and initial setup
- Environment variable configuration
- Development server startup
- First-time setup flow (sign up, sign in, create task, update profile)
- Testing flows for all features
- Troubleshooting common issues
- Development commands
- Project structure overview

**Agent Context Updated**:
- Added TypeScript 5.x with Next.js 16.0.1 (App Router) to CLAUDE.md
- Added Backend API integration details

## Outcome

- ✅ Impact: Created production-ready implementation plan with comprehensive research, architectural decisions, data models, API contracts, and quickstart guide. Plan provides clear roadmap for 44-57 tasks across 6 implementation phases.
- 🧪 Tests: N/A (planning phase - no code written)
- 📁 Files: Created 5 planning artifacts (plan.md, research.md, data-model.md, contracts/api-integration.md, quickstart.md) totaling 2800+ lines. Updated CLAUDE.md with new technologies.
- 🔁 Next prompts: /sp.tasks to generate detailed task breakdown from plan
- 🧠 Reflection: Comprehensive planning phase completed successfully. All technical decisions documented with rationale and alternatives considered. Research phase resolved all unknowns. Phase 1 deliverables provide complete foundation for implementation. Plan balances preserving existing frontend design with adding comprehensive functionality. Ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all deliverables
- Graders run and results (PASS/FAIL): Constitution Check - ALL GATES PASSED
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
