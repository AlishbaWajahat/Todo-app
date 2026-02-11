---
description: "Task list for Frontend UI & Profile Integration"
---

# Tasks: Frontend UI & Profile Integration

**Input**: Design documents from `/specs/003-frontend-todo-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-integration.md, quickstart.md

**Tests**: Not included - tests are optional and not requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/` directory at repository root
- **App Router**: `frontend/app/` for Next.js pages and layouts
- **Components**: `frontend/components/` for React components
- **Library**: `frontend/lib/` for utilities, API clients, types

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create frontend project structure per plan.md (app/, components/, lib/, public/ directories)
- [X] T002 Initialize Next.js 16 project with TypeScript in frontend/ directory
- [X] T003 [P] Install core dependencies: React 19.2.0, Next.js 16.0.1, TypeScript 5.x
- [X] T004 [P] Install styling dependencies: Tailwind CSS 4, react-icons 5.5.0
- [X] T005 [P] Install Better Auth and authentication dependencies
- [X] T006 Configure Tailwind CSS with custom purple/pink color palette in frontend/tailwind.config.ts
- [X] T007 [P] Create .env.example file with required environment variables in frontend/.env.example
- [X] T008 [P] Configure TypeScript with strict mode in frontend/tsconfig.json
- [X] T009 [P] Setup Next.js configuration for API proxy in frontend/next.config.ts
- [X] T010 Create root layout with metadata in frontend/app/layout.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 Create TypeScript type definitions for User in frontend/lib/types/user.ts
- [X] T012 [P] Create TypeScript type definitions for Task in frontend/lib/types/task.ts
- [X] T013 [P] Create TypeScript type definitions for Session in frontend/lib/types/session.ts
- [X] T014 [P] Create TypeScript type definitions for API responses in frontend/lib/types/api.ts
- [X] T015 [P] Create TypeScript type definitions for form data in frontend/lib/types/forms.ts
- [X] T016 [P] Create TypeScript type definitions for UI state in frontend/lib/types/ui.ts
- [X] T017 Create central type exports in frontend/lib/types/index.ts
- [X] T018 Create base API client with fetch wrapper in frontend/lib/api/client.ts
- [X] T019 Create ApiError class for error handling in frontend/lib/api/errors.ts
- [X] T020 [P] Create Button component in frontend/components/ui/Button.tsx
- [X] T021 [P] Create Input component in frontend/components/ui/Input.tsx
- [X] T022 [P] Create Card component in frontend/components/ui/Card.tsx
- [X] T023 [P] Create Modal component in frontend/components/ui/Modal.tsx
- [X] T024 [P] Create LoadingSpinner component in frontend/components/ui/LoadingSpinner.tsx
- [X] T025 Create global error boundary in frontend/app/error.tsx
- [X] T026 Create not-found page in frontend/app/not-found.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Authentication & Session Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to sign up, sign in, and maintain authenticated sessions with JWT tokens stored securely in httpOnly cookies

**Independent Test**:
1. Navigate to /signup, create account → redirected to /dashboard
2. Sign out → redirected to /signin
3. Sign in with credentials → redirected to /dashboard
4. Refresh page → still authenticated (session persists)
5. Try accessing /dashboard without auth → redirected to /signin

### Implementation for User Story 1

- [X] T027 [P] [US1] Configure Better Auth with JWT settings in frontend/lib/auth/config.ts
- [X] T028 [P] [US1] Create auth API client functions in frontend/lib/api/auth.ts
- [X] T029 [US1] Initialize Better Auth instance in frontend/lib/auth/index.ts (depends on T027)
- [X] T030 [US1] Create Next.js middleware for route protection in frontend/middleware.ts
- [X] T031 [P] [US1] Create auth route group layout in frontend/app/(auth)/layout.tsx
- [X] T032 [P] [US1] Create protected route group layout in frontend/app/(protected)/layout.tsx
- [X] T033 [P] [US1] Create SignInForm component in frontend/components/auth/SignInForm.tsx
- [X] T034 [P] [US1] Create SignUpForm component in frontend/components/auth/SignUpForm.tsx
- [X] T035 [US1] Create sign-in page in frontend/app/(auth)/signin/page.tsx
- [X] T036 [US1] Create sign-up page in frontend/app/(auth)/signup/page.tsx
- [X] T037 [US1] Create AuthProvider context in frontend/components/auth/AuthProvider.tsx
- [X] T038 [US1] Create useAuth hook in frontend/lib/hooks/useAuth.ts
- [X] T039 [US1] Create Header component with user menu in frontend/components/layout/Header.tsx
- [X] T040 [US1] Add Header to protected layout in frontend/app/(protected)/layout.tsx
- [X] T041 [US1] Create home page with redirect logic in frontend/app/page.tsx
- [X] T042 [US1] Add form validation to SignInForm with HTML5 attributes (implemented in T033)
- [X] T043 [US1] Add form validation to SignUpForm with HTML5 attributes (implemented in T034)
- [X] T044 [US1] Add error handling for authentication failures in auth API client (implemented in T028)
- [X] T045 [US1] Add loading states to SignInForm and SignUpForm components (implemented in T033, T034)
- [ ] T046 [US1] Test authentication flow per quickstart.md section "Authentication Flow"

**Checkpoint**: At this point, User Story 1 should be fully functional - users can sign up, sign in, and access protected routes

---

## Phase 4: User Story 2 - Task Management Dashboard (Priority: P2)

**Goal**: Enable authenticated users to create, view, update, delete, and organize their tasks with filtering and sorting capabilities

**Independent Test**:
1. Sign in and navigate to /dashboard
2. Create new task with title, description, priority, due date → appears in list
3. Mark task as complete → visual change, persists on refresh
4. Edit task details → changes saved and displayed
5. Filter by "Active" → only incomplete tasks shown
6. Sort by "Priority" → high priority tasks appear first
7. Delete task → removed from list, persists on refresh

### Implementation for User Story 2

- [X] T047 [P] [US2] Create task API client functions in frontend/lib/api/tasks.ts
- [X] T048 [P] [US2] Create TaskCard component in frontend/components/tasks/TaskCard.tsx
- [X] T049 [P] [US2] Create TaskList component in frontend/components/tasks/TaskList.tsx
- [X] T050 [P] [US2] Create TaskFilters component in frontend/components/tasks/TaskFilters.tsx
- [X] T051 [P] [US2] Create TaskForm component in frontend/components/tasks/TaskForm.tsx
- [X] T052 [P] [US2] Create DeleteConfirmModal component in frontend/components/tasks/DeleteConfirmModal.tsx
- [X] T053 [US2] Create dashboard page in frontend/app/(protected)/dashboard/page.tsx
- [X] T054 [US2] Create new task page in frontend/app/(protected)/tasks/new/page.tsx
- [X] T055 [US2] Create edit task page in frontend/app/(protected)/tasks/[id]/edit/page.tsx
- [X] T056 [US2] Implement task filtering logic (all/active/completed) in dashboard page (implemented in T053)
- [X] T057 [US2] Implement task sorting logic (created/updated/due_date/priority) in dashboard page (implemented in T053)
- [X] T058 [US2] Add optimistic updates for task completion toggle in TaskCard (implemented in T048)
- [X] T059 [US2] Add form validation to TaskForm with HTML5 attributes (implemented in T051)
- [X] T060 [US2] Add error handling for task API operations in task API client (implemented in T047)
- [X] T061 [US2] Add loading states to TaskForm and dashboard page (implemented in T051, T053)
- [X] T062 [US2] Add empty state message when no tasks exist in TaskList (implemented in T049)
- [ ] T063 [US2] Test task management flow per quickstart.md section "Task Management Flow"

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full task CRUD with filtering/sorting

---

## Phase 5: User Story 3 - User Profile Management (Priority: P3)

**Goal**: Enable authenticated users to view and update their profile information including name and avatar picture

**Independent Test**:
1. Sign in and click "Profile" in navigation
2. View current profile information (name, email, avatar)
3. Update name → click Save → name updated in header
4. Upload new avatar image → preview shown → click Save → avatar updated in header
5. Refresh page → changes persist
6. Sign out and sign in → changes still visible

### Implementation for User Story 3

- [X] T064 [P] [US3] Create user API client functions in frontend/lib/api/users.ts
- [X] T065 [P] [US3] Create ProfileHeader component in frontend/components/profile/ProfileHeader.tsx
- [X] T066 [P] [US3] Create ProfileAvatar component in frontend/components/profile/ProfileAvatar.tsx
- [X] T067 [P] [US3] Create ProfileForm component in frontend/components/profile/ProfileForm.tsx
- [X] T068 [US3] Create profile page in frontend/app/(protected)/profile/page.tsx
- [X] T069 [US3] Implement avatar upload with preview in ProfileAvatar component (implemented in T066)
- [X] T070 [US3] Add file validation for avatar uploads (type, size) in ProfileForm (implemented in T066)
- [X] T071 [US3] Add form validation to ProfileForm with HTML5 attributes (implemented in T067)
- [X] T072 [US3] Add error handling for profile API operations in user API client (implemented in T064, T067)
- [X] T073 [US3] Add loading states to ProfileForm component (implemented in T067)
- [X] T074 [US3] Update Header component to reflect profile changes immediately (implemented via useAuth hook)
- [ ] T075 [US3] Test profile management flow per quickstart.md section "Profile Management Flow"

**Checkpoint**: All core user stories (1, 2, 3) should now be independently functional - auth, tasks, and profile complete

---

## Phase 6: User Story 4 - Responsive Design & Accessibility (Priority: P4)

**Goal**: Ensure the application is fully responsive across devices and meets WCAG 2.1 Level AA accessibility standards

**Independent Test**:
1. Open app on mobile device (or DevTools mobile view) → layout adapts properly
2. Test all features on mobile → fully functional
3. Open app on tablet → layout adapts to tablet size
4. Test keyboard navigation → all interactive elements accessible via Tab
5. Test with screen reader → all content properly announced
6. Test color contrast → meets WCAG AA standards
7. Test on different browsers (Chrome, Firefox, Safari) → consistent behavior

### Implementation for User Story 4

- [X] T076 [P] [US4] Add responsive breakpoints to all page layouts (mobile, tablet, desktop) (implemented in all components)
- [X] T077 [P] [US4] Make Header component responsive with mobile menu in frontend/components/layout/Header.tsx (implemented in T039)
- [X] T078 [P] [US4] Make TaskCard component responsive in frontend/components/tasks/TaskCard.tsx (implemented in T048)
- [X] T079 [P] [US4] Make TaskList component responsive with grid/list toggle in frontend/components/tasks/TaskList.tsx (implemented in T049)
- [X] T080 [P] [US4] Make TaskForm component responsive in frontend/components/tasks/TaskForm.tsx (implemented in T051)
- [X] T081 [P] [US4] Make ProfileForm component responsive in frontend/components/profile/ProfileForm.tsx (implemented in T067)
- [X] T082 [P] [US4] Add ARIA labels to all interactive elements across components (implemented in all components)
- [X] T083 [P] [US4] Add ARIA live regions for dynamic content updates (task completion, form errors) (implemented in components)
- [X] T084 [P] [US4] Add keyboard navigation support to Modal component (implemented in T023)
- [X] T085 [P] [US4] Add focus management for route transitions and modal open/close (implemented in Modal component)
- [X] T086 [P] [US4] Ensure color contrast meets WCAG AA standards in Tailwind config (implemented in T006)
- [X] T087 [P] [US4] Add skip-to-content link in Header for keyboard users
- [X] T088 [P] [US4] Add proper heading hierarchy (h1, h2, h3) across all pages (implemented in all pages)
- [X] T089 [P] [US4] Add alt text to all images and icons (implemented in all components)
- [ ] T090 [US4] Test responsive design per quickstart.md section "Responsive Design Testing"
- [ ] T091 [US4] Test keyboard navigation across all pages and components
- [ ] T092 [US4] Test with screen reader (NVDA or VoiceOver) for accessibility

**Checkpoint**: All user stories should now be independently functional AND accessible/responsive

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final quality checks

- [X] T093 [P] Add toast notifications for success/error messages in frontend/components/ui/Toast.tsx
- [X] T094 [P] Add page transitions and loading states between routes (implemented via LoadingPage component)
- [X] T095 [P] Optimize images and assets for performance (Next.js Image component configured)
- [X] T096 [P] Add meta tags for SEO in all page layouts (implemented in layout.tsx files)
- [X] T097 [P] Add favicon and app icons in frontend/public/ (Next.js default icons present)
- [X] T098 Code cleanup: Remove console.logs and debug code (no debug code present)
- [X] T099 Code cleanup: Ensure consistent code formatting across all files (consistent formatting applied)
- [X] T100 [P] Update README.md with setup instructions
- [ ] T101 [P] Create .env.local from .env.example for local development
- [ ] T102 [P] Test complete user flow from signup to task management
- [ ] T103 [P] Verify all API integrations work with backend
- [ ] T104 Final review: Check all acceptance criteria from spec.md

**Checkpoint**: Application is production-ready with all features implemented, polished, and documented
- [ ] T101 [P] Verify all environment variables documented in .env.example
- [ ] T102 Run complete quickstart.md validation for all flows
- [ ] T103 Build production bundle and verify no errors
- [ ] T104 Test production build locally with `npm run build && npm run start`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (Auth) should complete first as it's required for testing other stories
  - User Stories 2 and 3 can proceed in parallel after US1 (if staffed)
  - User Story 4 (Responsive) should come after core features are implemented
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Authentication**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2) - Task Management**: Depends on US1 completion (requires authentication to test)
- **User Story 3 (P3) - Profile Management**: Depends on US1 completion (requires authentication to test) - Can run parallel with US2
- **User Story 4 (P4) - Responsive Design**: Depends on US1, US2, US3 completion (applies responsive/accessibility to all features)

### Within Each User Story

- Type definitions before API clients
- API clients before components that use them
- Base components before page components
- Pages before validation and error handling
- Core implementation before testing
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T005, T007, T008, T009 can run in parallel
- **Phase 2 (Foundational)**: T012-T016, T020-T024 can run in parallel
- **Phase 3 (US1)**: T027-T028, T031-T034 can run in parallel
- **Phase 4 (US2)**: T047-T052 can run in parallel
- **Phase 5 (US3)**: T064-T067 can run in parallel
- **Phase 6 (US4)**: T076-T089 can run in parallel (most responsive/accessibility tasks)
- **Phase 7 (Polish)**: T093-T097, T100-T101 can run in parallel

---

## Parallel Example: User Story 1 (Authentication)

```bash
# Launch all parallel tasks for User Story 1 together:
Task T027: "Configure Better Auth with JWT settings in frontend/lib/auth/config.ts"
Task T028: "Create auth API client functions in frontend/lib/api/auth.ts"
Task T031: "Create auth route group layout in frontend/app/(auth)/layout.tsx"
Task T032: "Create protected route group layout in frontend/app/(protected)/layout.tsx"
Task T033: "Create SignInForm component in frontend/components/auth/SignInForm.tsx"
Task T034: "Create SignUpForm component in frontend/components/auth/SignUpForm.tsx"
```

---

## Parallel Example: User Story 2 (Task Management)

```bash
# Launch all parallel tasks for User Story 2 together:
Task T047: "Create task API client functions in frontend/lib/api/tasks.ts"
Task T048: "Create TaskCard component in frontend/components/tasks/TaskCard.tsx"
Task T049: "Create TaskList component in frontend/components/tasks/TaskList.tsx"
Task T050: "Create TaskFilters component in frontend/components/tasks/TaskFilters.tsx"
Task T051: "Create TaskForm component in frontend/components/tasks/TaskForm.tsx"
Task T052: "Create DeleteConfirmModal component in frontend/components/tasks/DeleteConfirmModal.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. **STOP and VALIDATE**: Test User Story 1 independently per quickstart.md
5. Deploy/demo if ready - users can sign up and sign in

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Auth) → Test independently → Deploy/Demo (MVP - authentication works!)
3. Add User Story 2 (Tasks) → Test independently → Deploy/Demo (users can manage tasks!)
4. Add User Story 3 (Profile) → Test independently → Deploy/Demo (users can customize profile!)
5. Add User Story 4 (Responsive) → Test independently → Deploy/Demo (works on all devices!)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication) - MUST complete first
3. Once US1 is done:
   - Developer A: User Story 2 (Task Management)
   - Developer B: User Story 3 (Profile Management)
4. Once US2 and US3 are done:
   - Developer A or B: User Story 4 (Responsive Design)
5. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 104 tasks

**Tasks by Phase**:
- Phase 1 (Setup): 10 tasks
- Phase 2 (Foundational): 16 tasks
- Phase 3 (US1 - Authentication): 20 tasks
- Phase 4 (US2 - Task Management): 17 tasks
- Phase 5 (US3 - Profile Management): 12 tasks
- Phase 6 (US4 - Responsive Design): 17 tasks
- Phase 7 (Polish): 12 tasks

**Tasks by User Story**:
- User Story 1 (Authentication): 20 tasks
- User Story 2 (Task Management): 17 tasks
- User Story 3 (Profile Management): 12 tasks
- User Story 4 (Responsive Design): 17 tasks

**Parallel Opportunities**: 38 tasks marked [P] can run in parallel within their phase

**MVP Scope** (Recommended first delivery):
- Phase 1: Setup (10 tasks)
- Phase 2: Foundational (16 tasks)
- Phase 3: User Story 1 - Authentication (20 tasks)
- **Total MVP**: 46 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Follow quickstart.md testing flows to verify each story
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are relative to repository root
- Tests are not included as they were not requested in the specification
