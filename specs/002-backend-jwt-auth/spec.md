# Feature Specification: Backend JWT Authentication & API Security

**Feature Branch**: `002-backend-jwt-auth`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "Authentication & API Security – JWT Enforcement with Users Table"

## Clarifications

### Session 2026-02-05

- Q: Should the backend update user profile data (email, name) from the JWT on every authentication, or only set it once during initial provisioning? → A: Manual update only - user data updates require explicit API calls (future feature)
- Q: Which JWT claim should the backend use to extract the unique user identifier, and what fallback strategy should be used if the expected claim is missing? → A: Use "sub" claim as primary user ID; reject token if missing
- Q: What authentication events should the backend log for operational and security purposes? → A: Log failures only - record failed authentication attempts and token validation errors

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure API Access with JWT Tokens (Priority: P1)

A developer integrating with the Todo API must authenticate all requests using JWT tokens issued by Better Auth. When making API calls without a valid token, the system immediately rejects the request with a clear authentication error. When providing a valid token, the API processes the request and returns data belonging only to that authenticated user.

**Why this priority**: This is the foundation of the entire security model. Without proper JWT enforcement, all other security measures are meaningless. This protects user data from unauthorized access and ensures compliance with basic security standards expected by hackathon reviewers.

**Independent Test**: Can be fully tested by making API requests with and without JWT tokens, verifying that unauthenticated requests are rejected with HTTP 401 and authenticated requests succeed with proper user isolation.

**Acceptance Scenarios**:

1. **Given** an API endpoint exists, **When** a request is made without an Authorization header, **Then** the system returns HTTP 401 Unauthorized with error message "Authentication required"
2. **Given** an API endpoint exists, **When** a request is made with an invalid JWT token, **Then** the system returns HTTP 401 Unauthorized with error message "Invalid or expired token"
3. **Given** an API endpoint exists, **When** a request is made with a valid JWT token, **Then** the system extracts the user identity from the token and processes the request
4. **Given** a valid JWT token for User A, **When** User A requests their tasks, **Then** the system returns only tasks belonging to User A
5. **Given** a valid JWT token, **When** the token has expired, **Then** the system returns HTTP 401 Unauthorized with error message "Token expired"

---

### User Story 2 - Automatic User Profile Provisioning (Priority: P2)

When a user authenticates for the first time using a JWT token issued by Better Auth, the backend automatically creates a corresponding user record in the `users` table. This ensures every authenticated user has a profile that can be used for future features like user preferences, profile management, and analytics.

**Why this priority**: This enables future frontend features (Spec 3) without requiring backend modifications. It establishes the user identity foundation needed for profile management, user preferences, and multi-user features. Without this, the frontend would have no way to display or manage user profiles.

**Independent Test**: Can be fully tested by authenticating with a new user's JWT token and verifying that a user record is automatically created in the database with information extracted from the JWT (user ID, email, name).

**Acceptance Scenarios**:

1. **Given** a new user authenticates with a valid JWT token, **When** the backend processes the first request, **Then** a new user record is created in the `users` table with data from the JWT
2. **Given** an existing user authenticates with a valid JWT token, **When** the backend processes the request, **Then** no duplicate user record is created
3. **Given** a JWT token contains user information (ID, email, name), **When** a user record is provisioned, **Then** all available information from the JWT is stored in the `users` table
4. **Given** a user record exists, **When** the user authenticates again, **Then** the existing record is used without modification (profile updates require explicit API calls in future features)

---

### User Story 3 - Strict Task Data Isolation (Priority: P3)

Users can only access, modify, or delete their own tasks. When User A attempts to access a task belonging to User B (even with a valid task ID), the system treats it as if the task doesn't exist, preventing any information leakage about other users' data.

**Why this priority**: This prevents cross-user data access vulnerabilities, which would be a critical security flaw. It ensures that even if a user guesses or discovers another user's task ID, they cannot access that data. This is essential for multi-user applications and demonstrates proper security practices to hackathon reviewers.

**Independent Test**: Can be fully tested by creating tasks for two different users, then attempting to access User B's tasks using User A's JWT token, verifying that the system returns 404 Not Found (not 403 Forbidden, to avoid information leakage).

**Acceptance Scenarios**:

1. **Given** User A is authenticated, **When** User A requests a task that belongs to User B, **Then** the system returns HTTP 404 Not Found
2. **Given** User A is authenticated, **When** User A attempts to update a task belonging to User B, **Then** the system returns HTTP 404 Not Found
3. **Given** User A is authenticated, **When** User A attempts to delete a task belonging to User B, **Then** the system returns HTTP 404 Not Found
4. **Given** User A is authenticated, **When** User A lists all tasks, **Then** the system returns only tasks where user_id matches User A's ID
5. **Given** User A is authenticated, **When** User A creates a new task, **Then** the task is automatically associated with User A's ID

---

### Edge Cases

- What happens when a JWT token is valid but the user ID in the token doesn't exist in the database? (System should auto-provision the user)
- What happens when a JWT token is malformed or uses an incorrect signing algorithm? (System should reject with HTTP 401 and log the failure)
- What happens when the JWT secret key is not configured? (System should fail to start with a clear error message)
- What happens when a user's JWT token is valid but they attempt to access a non-existent task ID? (System should return HTTP 404)
- What happens when multiple requests arrive simultaneously for a new user? (System should handle race conditions gracefully, ensuring only one user record is created)
- What happens when the JWT contains minimal information (only user ID in "sub" claim, no email or name)? (System should provision user with available data only)
- What happens when the JWT is missing the "sub" claim? (System should reject with HTTP 401 and log the failure)
- What happens when the database connection fails during user provisioning? (System should return HTTP 500 and not proceed with the request)
- What happens when a user's email or name changes in Better Auth after initial provisioning? (User profile data remains unchanged; updates require explicit API calls in future features)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate JWT tokens on every API request before processing
- **FR-002**: System MUST extract user identity from validated JWT tokens using the "sub" claim as the unique user ID, and reject tokens missing the "sub" claim
- **FR-003**: System MUST reject requests without an Authorization header with HTTP 401 Unauthorized
- **FR-004**: System MUST reject requests with invalid, expired, or malformed JWT tokens with HTTP 401 Unauthorized
- **FR-005**: System MUST verify JWT token signatures using the shared secret key from Better Auth
- **FR-006**: System MUST automatically create a user record in the `users` table on first authentication if the user doesn't exist
- **FR-007**: System MUST handle race conditions during user provisioning to prevent duplicate user records
- **FR-008**: System MUST filter all task queries by the authenticated user's ID
- **FR-009**: System MUST return HTTP 404 Not Found when a user attempts to access another user's task (not 403 Forbidden, to prevent information leakage)
- **FR-010**: System MUST automatically associate new tasks with the authenticated user's ID
- **FR-011**: System MUST prevent modification or deletion of tasks belonging to other users
- **FR-012**: System MUST remain stateless, deriving all user identity from JWT tokens without server-side sessions
- **FR-013**: System MUST provide clear, actionable error messages for authentication failures
- **FR-014**: System MUST fail to start if the JWT secret key is not configured in environment variables
- **FR-015**: System MUST support JWT tokens with standard claims (sub, email, name, exp, iat)
- **FR-016**: System MUST log all authentication failures including failed token validation attempts, missing tokens, expired tokens, and invalid signatures for security monitoring and debugging

### Key Entities

- **User**: Represents an authenticated user in the system. Contains user ID (from JWT), email, name, and timestamps for account creation and last update. This entity is automatically provisioned from JWT token data on first authentication.

- **Task**: Represents a todo item belonging to a specific user. Contains task details (title, description, status, priority, due date) and a foreign key reference to the owning user. All task operations are scoped to the authenticated user.

- **JWT Token**: External entity issued by Better Auth. Contains user identity claims (user ID, email, name) and standard JWT claims (expiration, issued at). The backend validates and extracts data from these tokens but does not issue them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of API endpoints require valid JWT authentication (zero unauthenticated endpoints accessible)
- **SC-002**: Authentication validation adds less than 50ms latency to API response times
- **SC-003**: Zero cross-user data access incidents (users can only access their own tasks)
- **SC-004**: User provisioning succeeds on first authentication for 100% of valid JWT tokens
- **SC-005**: Invalid authentication attempts return appropriate HTTP 401 responses with clear error messages within 100ms
- **SC-006**: System handles 1000 concurrent authenticated requests without authentication failures
- **SC-007**: Backend remains fully stateless (no server-side session storage required)
- **SC-008**: All task operations complete successfully when authenticated, with user isolation enforced
- **SC-009**: System startup fails immediately with clear error if JWT secret is not configured
- **SC-010**: Race conditions during user provisioning result in exactly one user record (no duplicates)

## Assumptions

- Better Auth is configured and issuing JWT tokens with standard claims including "sub" for user ID, and optionally email, name, exp, iat
- The JWT "sub" claim contains the unique user identifier and is present in all tokens
- The JWT secret key used by Better Auth is available to the FastAPI backend via environment variables
- JWT tokens use HS256 (HMAC with SHA-256) signing algorithm
- The `users` table schema supports storing user ID, email, name, created_at, and updated_at fields
- User profile data (email, name) is set only during initial provisioning and does not update on subsequent authentications
- The `tasks` table has a user_id foreign key column referencing the users table
- The existing FastAPI backend has task CRUD endpoints that need to be secured
- Network communication between frontend and backend is over HTTPS in production
- JWT tokens have a reasonable expiration time (e.g., 1-24 hours) set by Better Auth
- The backend has access to a JWT library for token validation and decoding
- Database transactions are supported for atomic user provisioning operations
- Authentication failures are logged for security monitoring and debugging purposes

## Dependencies

- Better Auth must be configured and operational (external dependency)
- JWT secret key must be shared between Better Auth and FastAPI backend
- Database schema must include `users` table with appropriate columns
- Database schema must include user_id foreign key in `tasks` table
- Python JWT library (e.g., python-jose, PyJWT) must be available
- Environment variable configuration system must be in place

## Out of Scope

- Implementation of Better Auth itself (external system)
- Frontend authentication UI (login/signup forms)
- JWT token issuance or refresh logic (handled by Better Auth)
- Password hashing or credential storage (handled by Better Auth)
- OAuth provider integration (handled by Better Auth)
- User profile update endpoints (future Spec 3)
- Email verification or password reset flows
- Role-based access control (RBAC) or permissions beyond user isolation
- API rate limiting or throttling
- Comprehensive audit logging of all authentication events (only authentication failures are logged)
- Multi-factor authentication (MFA)
- Token revocation or blacklisting mechanisms

## Notes

This specification focuses exclusively on securing the existing FastAPI backend with JWT authentication and establishing the foundation for multi-user functionality. The authentication mechanism relies on JWT tokens issued by Better Auth, with the backend responsible only for validation and user identity extraction.

The lazy user provisioning approach (creating user records on first authentication) ensures that the backend can operate independently while maintaining data consistency. This design allows the frontend to be developed separately (Spec 3) without requiring backend changes.

Security is prioritized through strict user isolation at the database query level, ensuring that even with valid authentication, users cannot access data belonging to others. The use of HTTP 404 (instead of 403) for unauthorized task access prevents information leakage about the existence of other users' tasks.

The stateless design ensures scalability and simplifies deployment, as no server-side session management is required. All user identity is derived from the JWT token on each request, making the backend suitable for serverless and containerized environments.
