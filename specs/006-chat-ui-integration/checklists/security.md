# Security Checklist - Chat UI & End-to-End Integration

## Authentication & Authorization

- [ ] Chat page requires user to be logged in
- [ ] Unauthenticated users are redirected to login page
- [ ] JWT token is included in all agent API requests
- [ ] JWT token is passed securely in Authorization header (Bearer token)
- [ ] Token expiry is detected and handled gracefully
- [ ] User is prompted to log in again when token expires
- [ ] Token is not exposed in console logs
- [ ] Token is not exposed in error messages
- [ ] Token is not exposed in URL parameters

## User Isolation

- [ ] All chat requests include authenticated user's ID
- [ ] User can only view their own tasks via chat
- [ ] User can only create tasks in their own account
- [ ] User can only complete their own tasks
- [ ] User can only update their own tasks
- [ ] User can only delete their own tasks
- [ ] Cross-user task access attempts return "Task not found" error
- [ ] No information leakage about other users' tasks in error messages

## Input Validation & Sanitization

- [ ] User input is validated before sending to agent
- [ ] Empty messages are prevented or rejected
- [ ] Very long messages (>1000 chars) are truncated or rejected
- [ ] Special characters in user input are handled safely
- [ ] SQL injection attempts in task titles are prevented
- [ ] XSS attempts in task titles are prevented (e.g., <script> tags)
- [ ] HTML injection in user input is prevented
- [ ] User input is sanitized before rendering in UI

## Output Sanitization

- [ ] Agent responses are sanitized before rendering
- [ ] HTML tags in agent responses are escaped or stripped
- [ ] JavaScript code in agent responses cannot execute
- [ ] Special characters in agent responses render safely
- [ ] Task titles with malicious content display safely
- [ ] Error messages don't expose internal system details
- [ ] Stack traces are never visible to users
- [ ] Database connection strings are never exposed
- [ ] API keys are never exposed in responses

## Network Security

- [ ] All API requests use HTTPS (in production)
- [ ] CORS is properly configured on backend
- [ ] API endpoints validate request origin
- [ ] Rate limiting is implemented to prevent abuse
- [ ] Request size limits are enforced
- [ ] Timeout limits are enforced (30 seconds max)

## Data Privacy

- [ ] Chat messages are not persisted to database
- [ ] Chat history is cleared when user logs out
- [ ] Chat history is cleared when user navigates away
- [ ] No sensitive data is logged to console
- [ ] No sensitive data is stored in localStorage (except JWT)
- [ ] User data is only accessible to authenticated user
