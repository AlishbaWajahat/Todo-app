# Quickstart Guide: Backend JWT Authentication & API Security

**Feature**: Backend JWT Authentication & API Security
**Date**: 2026-02-05
**Purpose**: Setup instructions and testing guide for developers

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (Neon Serverless recommended)
- Better Auth configured and issuing JWT tokens
- Git for version control

## Environment Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Required packages** (add to `requirements.txt` if not present):
```
fastapi>=0.104.0
sqlmodel>=0.0.14
python-jose[cryptography]>=3.3.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
uvicorn[standard]>=0.24.0
alembic>=1.12.0
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/database

# JWT Configuration
JWT_SECRET=your-secret-key-must-match-better-auth
JWT_ALGORITHM=HS256

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

**Important**:
- `JWT_SECRET` must be identical to the secret used by Better Auth
- `JWT_SECRET` should be a strong random string (minimum 32 characters)
- Never commit `.env` to version control

Create `.env.example` for documentation:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/database

# JWT Configuration (MUST match Better Auth secret)
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 3. Database Migrations

Initialize Alembic (if not already done):

```bash
cd backend
alembic init alembic
```

Create migration for users table:

```bash
alembic revision -m "create_users_table"
```

Create migration for adding user_id to tasks:

```bash
alembic revision -m "add_user_id_to_tasks"
```

Apply migrations:

```bash
alembic upgrade head
```

Verify migrations:

```bash
alembic current
alembic history
```

### 4. Start the Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server should start at: `http://localhost:8000`

API documentation available at: `http://localhost:8000/docs`

## Testing the API

### Manual Testing via FastAPI Docs

1. **Open API Documentation**
   - Navigate to `http://localhost:8000/docs`
   - You'll see the interactive Swagger UI

2. **Obtain a JWT Token**
   - Use Better Auth to sign up/sign in
   - Copy the JWT token from the authentication response
   - Example token format: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

3. **Authorize in Swagger UI**
   - Click the "Authorize" button (lock icon) at the top right
   - Enter: `Bearer <your-jwt-token>`
   - Click "Authorize"
   - Click "Close"

4. **Test Endpoints**

   **Create a Task**:
   - Expand `POST /tasks`
   - Click "Try it out"
   - Enter request body:
     ```json
     {
       "title": "Test task",
       "description": "Testing JWT authentication",
       "priority": "high"
     }
     ```
   - Click "Execute"
   - Expected response: `201 Created` with task details

   **Get All Tasks**:
   - Expand `GET /tasks`
   - Click "Try it out"
   - Click "Execute"
   - Expected response: `200 OK` with array of tasks (only your tasks)

   **Get Single Task**:
   - Expand `GET /tasks/{task_id}`
   - Click "Try it out"
   - Enter task ID (e.g., `1`)
   - Click "Execute"
   - Expected response: `200 OK` with task details (if you own it)
   - Expected response: `404 Not Found` (if owned by another user)

   **Update a Task**:
   - Expand `PUT /tasks/{task_id}`
   - Click "Try it out"
   - Enter task ID and update data:
     ```json
     {
       "completed": true
     }
     ```
   - Click "Execute"
   - Expected response: `200 OK` with updated task

   **Delete a Task**:
   - Expand `DELETE /tasks/{task_id}`
   - Click "Try it out"
   - Enter task ID
   - Click "Execute"
   - Expected response: `204 No Content`

### Testing Authentication Failures

1. **Missing Token**:
   - Click "Authorize" and remove the token
   - Try any endpoint
   - Expected response: `401 Unauthorized`
   - Error message: "Authentication required"

2. **Invalid Token**:
   - Click "Authorize" and enter: `Bearer invalid-token`
   - Try any endpoint
   - Expected response: `401 Unauthorized`
   - Error message: "Invalid or expired token"

3. **Expired Token**:
   - Use an expired JWT token
   - Try any endpoint
   - Expected response: `401 Unauthorized`
   - Error message: "Invalid or expired token"

### Testing User Isolation

1. **Create tasks with User A's token**:
   - Authorize with User A's JWT token
   - Create 2-3 tasks
   - Note the task IDs

2. **Switch to User B's token**:
   - Authorize with User B's JWT token
   - Try to get User A's tasks by ID
   - Expected response: `404 Not Found`
   - Error message: "Task not found or you don't have permission to access it"

3. **Verify task lists are isolated**:
   - Get all tasks with User A's token → should see User A's tasks only
   - Get all tasks with User B's token → should see User B's tasks only
   - No overlap between task lists

### Testing User Provisioning

1. **First-time user authentication**:
   - Create a new user in Better Auth
   - Obtain JWT token for the new user
   - Make any API request (e.g., `GET /tasks`)
   - Check database: `SELECT * FROM users WHERE id = '<user_id_from_jwt>';`
   - Expected: User record exists with data from JWT (id, email, name)

2. **Subsequent authentications**:
   - Make another API request with the same user's token
   - Check database: User record unchanged (no duplicate, no updates)
   - Expected: Same user record, no new rows created

3. **Race condition test** (optional, requires concurrent requests):
   - Send 10 simultaneous requests with a new user's token
   - Check database: Only 1 user record created
   - Expected: No duplicate users, all requests succeed

## Testing with cURL

### Get All Tasks

```bash
curl -X GET "http://localhost:8000/tasks" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json"
```

### Create a Task

```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task from cURL",
    "description": "Testing API with cURL",
    "priority": "medium"
  }'
```

### Get Single Task

```bash
curl -X GET "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json"
```

### Update a Task

```bash
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

### Delete a Task

```bash
curl -X DELETE "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json"
```

### Test Authentication Failure

```bash
# Missing token
curl -X GET "http://localhost:8000/tasks" \
  -H "Content-Type: application/json"

# Expected: 401 Unauthorized

# Invalid token
curl -X GET "http://localhost:8000/tasks" \
  -H "Authorization: Bearer invalid-token" \
  -H "Content-Type: application/json"

# Expected: 401 Unauthorized
```

## Verification Checklist

Use this checklist to verify the implementation is complete and correct:

### Authentication
- [ ] All endpoints require JWT token (except health check if present)
- [ ] Requests without Authorization header return 401
- [ ] Requests with invalid token return 401
- [ ] Requests with expired token return 401
- [ ] Valid token allows access to endpoints

### User Provisioning
- [ ] First-time user authentication creates user record in database
- [ ] User record contains id, email, name from JWT
- [ ] Subsequent authentications reuse existing user record
- [ ] No duplicate user records created (race condition handled)

### User Isolation
- [ ] User A cannot access User B's tasks (returns 404)
- [ ] GET /tasks returns only authenticated user's tasks
- [ ] POST /tasks creates task with authenticated user's ID
- [ ] PUT /tasks only updates authenticated user's tasks
- [ ] DELETE /tasks only deletes authenticated user's tasks

### Error Handling
- [ ] 401 responses include meaningful error messages
- [ ] 404 responses don't leak information about other users' data
- [ ] Validation errors return 400 with field-level details
- [ ] Server errors return 500 with generic message (no stack traces)

### Security
- [ ] JWT_SECRET loaded from environment variable (not hardcoded)
- [ ] Database connection string from environment variable
- [ ] .env file in .gitignore
- [ ] .env.example documents all required variables
- [ ] Authentication failures logged for security monitoring

### Performance
- [ ] Authentication adds <50ms overhead per request
- [ ] Task queries complete in <10ms for typical user
- [ ] User provisioning completes in <5ms
- [ ] No N+1 query issues

### API Contract
- [ ] All endpoints follow RESTful conventions
- [ ] Response format consistent across endpoints
- [ ] Timestamps in ISO 8601 format
- [ ] Error responses include "detail" and "code" fields
- [ ] OpenAPI documentation accessible at /docs

## Troubleshooting

### Issue: 401 Unauthorized with valid token

**Possible causes**:
- JWT_SECRET mismatch between Better Auth and FastAPI backend
- Token expired (check `exp` claim)
- Token algorithm mismatch (ensure both use HS256)

**Solution**:
1. Verify JWT_SECRET matches in both systems
2. Check token expiration: `jwt.io` → paste token → check `exp` claim
3. Verify algorithm in Better Auth configuration

### Issue: User record not created on first authentication

**Possible causes**:
- Database connection failure
- Missing users table (migration not applied)
- JWT missing "sub" claim

**Solution**:
1. Check database connection: `psql $DATABASE_URL`
2. Verify migrations applied: `alembic current`
3. Decode JWT token and verify "sub" claim exists

### Issue: User can access another user's tasks

**Possible causes**:
- Missing user_id filter in query
- Incorrect user_id extracted from JWT

**Solution**:
1. Review query code: ensure `WHERE user_id = <authenticated_user_id>`
2. Add logging to verify user_id extracted from JWT
3. Check database: verify tasks have correct user_id values

### Issue: Duplicate user records created

**Possible causes**:
- Missing UNIQUE constraint on users.id
- Race condition not handled properly

**Solution**:
1. Verify database constraint: `\d users` in psql
2. Review user provisioning code: ensure IntegrityError handling
3. Add migration to add UNIQUE constraint if missing

## Next Steps

After verifying all checklist items pass:

1. **Generate Tasks**: Run `/sp.tasks` to break down implementation into atomic tasks
2. **Implement**: Execute tasks using appropriate agents (Auth Agent, Backend Agent, Database Agent)
3. **Security Audit**: Use Auth Agent to review authentication implementation
4. **Integration Test**: Test with actual Better Auth frontend
5. **Documentation**: Update README.md with setup instructions

## Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- python-jose Documentation: https://python-jose.readthedocs.io/
- JWT.io (token decoder): https://jwt.io/
- Neon PostgreSQL: https://neon.tech/docs
