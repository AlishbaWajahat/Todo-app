# Task Management API - Backend

Production-ready RESTful API for managing tasks with JWT authentication and persistent storage in Neon Serverless PostgreSQL.

## Overview

This backend API provides secure task management with:
- **JWT Authentication**: Token-based authentication using Better Auth
- **User Isolation**: Strict data isolation - users can only access their own tasks
- **Automatic User Provisioning**: Users are automatically created from JWT tokens on first authentication
- **RESTful Design**: Standard HTTP methods and status codes
- **Type Safety**: Full type hints with SQLModel and Pydantic
- **Auto Documentation**: Interactive API docs at `/docs`

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Deployment](#deployment)

## Prerequisites

- **Python 3.11+** (required for modern type hints)
- **Neon PostgreSQL** database account ([sign up here](https://neon.tech))
- **Better Auth** configured and issuing JWT tokens
- **pip** (Python package manager)

## Quick Start

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your actual values (DATABASE_URL, JWT_SECRET)

# 5. Run database migrations
alembic upgrade head

# 6. Start the server
uvicorn main:app --reload

# 7. Access API documentation
# Open http://localhost:8000/docs
```

## Environment Configuration

Create a `.env` file in the `backend/` directory with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host.neon.tech/database?sslmode=require

# JWT Configuration (MUST match Better Auth secret)
JWT_SECRET=your-secret-key-min-32-chars-change-this-in-production
JWT_ALGORITHM=HS256

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000"]

# Application Environment
ENVIRONMENT=development
```

**Critical Configuration Notes:**

1. **JWT_SECRET**: MUST be identical to the secret used by Better Auth in your frontend
   - Generate with: `openssl rand -hex 32`
   - Minimum 32 characters recommended
   - Never commit to version control

2. **DATABASE_URL**: Get from Neon dashboard
   - Format: `postgresql://user:password@host/database?sslmode=require`
   - Must include `?sslmode=require` for secure connections

3. **CORS_ORIGINS**: JSON array of allowed frontend URLs
   - Development: `["http://localhost:3000"]`
   - Production: `["https://yourdomain.com"]`

See `.env.example` for detailed documentation of all configuration options.

## Database Setup

### Initial Setup

The backend uses Alembic for database migrations. Migrations are already created in `alembic/versions/`.

```bash
# Apply all migrations
alembic upgrade head

# Verify current migration
alembic current

# View migration history
alembic history
```

### Database Schema

**Users Table:**
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,           -- User ID from JWT "sub" claim
    email VARCHAR UNIQUE NOT NULL,    -- User email
    name VARCHAR,                     -- User display name (optional)
    avatar_url VARCHAR,               -- Profile picture URL (optional)
    created_at TIMESTAMP NOT NULL,    -- When user was created
    updated_at TIMESTAMP NOT NULL     -- Last update timestamp
);
```

**Tasks Table:**
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10),             -- low, medium, high
    due_date TIMESTAMP,
    user_id VARCHAR NOT NULL,         -- Foreign key to users.id
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_id_id ON tasks(id, user_id);
```

## Running the Server

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload
```

Server starts at: `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

All endpoints require JWT authentication except `/health`.

### Base URL

```
http://localhost:8000/api/v1
```

### Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | No |
| GET | `/api/v1/tasks` | List all user's tasks | Yes |
| POST | `/api/v1/tasks` | Create a new task | Yes |
| GET | `/api/v1/tasks/{id}` | Get task by ID | Yes |
| PUT | `/api/v1/tasks/{id}` | Update task | Yes |
| DELETE | `/api/v1/tasks/{id}` | Delete task | Yes |

### Detailed Endpoint Documentation

#### 1. Health Check

```http
GET /health
```

**Description**: Check API health status (no authentication required)

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "service": "task-management-api",
  "version": "1.0.0"
}
```

**Example cURL:**
```bash
curl http://localhost:8000/health
```

---

#### 2. List Tasks

```http
GET /api/v1/tasks
```

**Description**: Get all tasks for the authenticated user

**Query Parameters:**
- `completed` (optional): Filter by completion status (`true` or `false`)
- `priority` (optional): Filter by priority (`low`, `medium`, `high`)

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "completed": false,
    "priority": "high",
    "due_date": "2026-02-10T00:00:00Z",
    "user_id": "user_123",
    "created_at": "2026-02-05T10:00:00Z",
    "updated_at": "2026-02-05T10:00:00Z"
  }
]
```

**Example cURL:**
```bash
# Get all tasks
curl -X GET "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"

# Filter by completed status
curl -X GET "http://localhost:8000/api/v1/tasks?completed=false" \
  -H "Authorization: Bearer <token>"

# Filter by priority
curl -X GET "http://localhost:8000/api/v1/tasks?priority=high" \
  -H "Authorization: Bearer <token>"
```

---

#### 3. Create Task

```http
POST /api/v1/tasks
```

**Description**: Create a new task for the authenticated user

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "priority": "high",
  "due_date": "2026-02-10T00:00:00Z"
}
```

**Required Fields:**
- `title` (string, max 200 chars)

**Optional Fields:**
- `description` (string)
- `priority` (string: `low`, `medium`, `high`)
- `due_date` (ISO 8601 datetime)

**Response**: `201 Created`
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "completed": false,
  "priority": "high",
  "due_date": "2026-02-10T00:00:00Z",
  "user_id": "user_123",
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:00:00Z"
}
```

**Headers:**
```
Location: /api/v1/tasks/1
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "priority": "high",
    "due_date": "2026-02-10T00:00:00Z"
  }'
```

---

#### 4. Get Task by ID

```http
GET /api/v1/tasks/{id}
```

**Description**: Get a specific task by ID (only if owned by authenticated user)

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "completed": false,
  "priority": "high",
  "due_date": "2026-02-10T00:00:00Z",
  "user_id": "user_123",
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:00:00Z"
}
```

**Error Response**: `404 Not Found`
```json
{
  "detail": "Task not found or you don't have permission to access it",
  "code": "TASK_NOT_FOUND"
}
```

**Example cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

---

#### 5. Update Task

```http
PUT /api/v1/tasks/{id}
```

**Description**: Update a task (partial update - only provided fields are updated)

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "priority": "medium",
  "due_date": "2026-02-15T00:00:00Z"
}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "priority": "medium",
  "due_date": "2026-02-15T00:00:00Z",
  "user_id": "user_123",
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T11:30:00Z"
}
```

**Example cURL:**
```bash
# Update single field
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Update multiple fields
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "priority": "low",
    "completed": true
  }'
```

---

#### 6. Delete Task

```http
DELETE /api/v1/tasks/{id}
```

**Description**: Delete a task (only if owned by authenticated user)

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response**: `204 No Content`

**Error Response**: `404 Not Found`
```json
{
  "detail": "Task not found or you don't have permission to access it",
  "code": "TASK_NOT_FOUND"
}
```

**Example cURL:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer <token>"
```

---

### Error Responses

All error responses follow this format:

```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

**Common Error Codes:**

| Status | Code | Description |
|--------|------|-------------|
| 401 | `MISSING_TOKEN` | No Authorization header provided |
| 401 | `INVALID_AUTH_HEADER` | Invalid Authorization header format |
| 401 | `TOKEN_EXPIRED` | JWT token has expired |
| 401 | `INVALID_TOKEN` | JWT token is invalid or signature mismatch |
| 401 | `MISSING_SUB_CLAIM` | JWT token missing "sub" claim |
| 401 | `AUTH_REQUIRED` | Authentication required but not provided |
| 404 | `TASK_NOT_FOUND` | Task not found or user doesn't have permission |
| 500 | `INTERNAL_ERROR` | Internal server error |
| 500 | `USER_PROVISIONING_FAILED` | Failed to create user profile |
| 500 | `AUTH_ERROR` | Authentication system error |

## Authentication

### JWT Token Format

The API expects JWT tokens issued by Better Auth in the following format:

**Header:**
```
Authorization: Bearer <jwt-token>
```

**Required JWT Claims:**
- `sub` (string): User ID (used as primary key in database)
- `exp` (number): Expiration timestamp

**Optional JWT Claims:**
- `email` (string): User email address
- `name` (string): User display name
- `iat` (number): Issued-at timestamp

### Authentication Flow

1. **User signs up/signs in** via Better Auth frontend
2. **Better Auth issues JWT token** with user information
3. **Frontend includes token** in Authorization header for API requests
4. **Backend validates token** signature and expiration
5. **Backend extracts user ID** from "sub" claim
6. **Backend provisions user** (creates user record on first authentication)
7. **Backend processes request** with user context

### User Provisioning

Users are automatically created in the database on first authentication:

- **Trigger**: First API request with a new user's JWT token
- **Data Source**: JWT token claims (sub, email, name)
- **Idempotency**: Subsequent requests reuse existing user record
- **Race Conditions**: Handled gracefully with database UNIQUE constraint

### Security Model

- **Stateless Authentication**: No server-side sessions
- **User Isolation**: All queries filtered by authenticated user ID
- **Information Hiding**: Returns 404 (not 403) for unauthorized access to prevent information leakage
- **Token Validation**: Every request validates JWT signature and expiration
- **Automatic Provisioning**: Users created lazily from trusted JWT tokens

## Testing

### Interactive Testing (Swagger UI)

1. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

2. **Open Swagger UI**
   - Navigate to http://localhost:8000/docs

3. **Obtain JWT Token**
   - Sign in via Better Auth frontend
   - Copy the JWT token from the response

4. **Authorize in Swagger**
   - Click "Authorize" button (lock icon)
   - Enter: `Bearer <your-jwt-token>`
   - Click "Authorize" then "Close"

5. **Test Endpoints**
   - Expand any endpoint
   - Click "Try it out"
   - Fill in parameters/body
   - Click "Execute"
   - View response

### Testing Authentication

**Test Missing Token:**
```bash
curl http://localhost:8000/api/v1/tasks
# Expected: 401 Unauthorized
```

**Test Invalid Token:**
```bash
curl -H "Authorization: Bearer invalid-token" \
  http://localhost:8000/api/v1/tasks
# Expected: 401 Unauthorized
```

**Test Valid Token:**
```bash
curl -H "Authorization: Bearer <valid-token>" \
  http://localhost:8000/api/v1/tasks
# Expected: 200 OK with task list
```

### Testing User Isolation

1. **Create tasks with User A's token**
2. **Switch to User B's token**
3. **Try to access User A's tasks**
4. **Expected**: 404 Not Found (user isolation working)

### Manual Testing Checklist

- [ ] Health check endpoint works without authentication
- [ ] All task endpoints require authentication
- [ ] Invalid/missing tokens return 401
- [ ] Users can only see their own tasks
- [ ] Users cannot access other users' tasks (404)
- [ ] First-time authentication creates user record
- [ ] Subsequent authentications reuse existing user
- [ ] Task creation sets correct user_id
- [ ] Task updates only work for owned tasks
- [ ] Task deletion only works for owned tasks

## Project Structure

```
backend/
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (gitignored)
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── alembic.ini               # Alembic configuration
│
├── alembic/                  # Database migrations
│   ├── env.py
│   └── versions/
│       ├── 53eb16208b05_create_users_table.py
│       └── 054ced276642_add_user_id_to_tasks.py
│
├── core/                     # Core application modules
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   └── database.py           # Database engine and session
│
├── models/                   # SQLModel database models
│   ├── __init__.py
│   ├── user.py               # User model
│   └── task.py               # Task model
│
├── schemas/                  # Pydantic request/response schemas
│   ├── __init__.py
│   ├── user.py               # User schemas
│   └── task.py               # Task schemas
│
├── middleware/               # Custom middleware
│   ├── __init__.py
│   └── auth.py               # JWT authentication middleware
│
├── dependencies/             # FastAPI dependencies
│   ├── __init__.py
│   └── auth.py               # Authentication dependencies
│
└── api/                      # API routes
    └── v1/                   # API version 1
        ├── __init__.py
        └── endpoints/
            ├── __init__.py
            └── tasks.py      # Task CRUD endpoints
```

## Security

### Security Features

- **JWT Authentication**: Token-based authentication with signature verification
- **User Isolation**: Strict data isolation at query level
- **No Hardcoded Secrets**: All secrets in environment variables
- **SQL Injection Protection**: Parameterized queries via SQLModel
- **Input Validation**: Pydantic schemas validate all inputs
- **Error Message Sanitization**: No stack traces or sensitive info in responses
- **CORS Configuration**: Configurable allowed origins
- **Authentication Logging**: All auth failures logged for monitoring

### Security Best Practices

1. **JWT_SECRET Management**
   - Use strong random string (min 32 chars)
   - Never commit to version control
   - Rotate periodically in production
   - Must match Better Auth secret

2. **Database Security**
   - Use SSL connections (`?sslmode=require`)
   - Store connection string in environment variable
   - Use connection pooling for efficiency

3. **CORS Configuration**
   - Specify exact frontend origins (no wildcards in production)
   - Update CORS_ORIGINS for production domains

4. **Error Handling**
   - Generic error messages to clients
   - Detailed logging for debugging
   - No stack traces exposed

5. **User Isolation**
   - All queries filter by authenticated user ID
   - Returns 404 (not 403) to prevent information leakage
   - User ID extracted from validated JWT (not request body)

## Troubleshooting

### Issue: 401 Unauthorized with valid token

**Possible Causes:**
- JWT_SECRET mismatch between Better Auth and backend
- Token expired
- Token algorithm mismatch

**Solutions:**
1. Verify JWT_SECRET matches in both systems
2. Check token expiration at [jwt.io](https://jwt.io)
3. Ensure both use HS256 algorithm

### Issue: Database connection failed

**Possible Causes:**
- Invalid DATABASE_URL
- Network connectivity issues
- Database not accessible

**Solutions:**
1. Verify DATABASE_URL format: `postgresql://user:password@host/db?sslmode=require`
2. Test connection: `psql $DATABASE_URL`
3. Check Neon dashboard for database status

### Issue: User record not created

**Possible Causes:**
- Database migration not applied
- JWT missing "sub" claim
- Database connection failure

**Solutions:**
1. Run migrations: `alembic upgrade head`
2. Verify JWT contains "sub" claim at [jwt.io](https://jwt.io)
3. Check database connection and logs

### Issue: CORS errors from frontend

**Possible Causes:**
- Frontend origin not in CORS_ORIGINS
- Invalid JSON format in CORS_ORIGINS

**Solutions:**
1. Add frontend URL to CORS_ORIGINS: `["http://localhost:3000"]`
2. Ensure JSON array format (with quotes)
3. Restart server after changing .env

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use different port
uvicorn main:app --port 8001

# Or kill existing process
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -ti:8000 | xargs kill
```

## Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Use production DATABASE_URL
- [ ] Generate strong JWT_SECRET (min 32 chars)
- [ ] Verify JWT_SECRET matches Better Auth
- [ ] Update CORS_ORIGINS with production domain(s)
- [ ] Enable HTTPS (required for production)
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Test authentication flow end-to-end
- [ ] Verify user isolation works correctly
- [ ] Set up health check monitoring
- [ ] Configure rate limiting (recommended)

### Recommended Hosting Platforms

- **Backend**: Railway, Render, Fly.io, AWS Lambda, Google Cloud Run
- **Database**: Neon PostgreSQL (already configured)
- **Monitoring**: Sentry, DataDog, New Relic

### Production Server Command

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Workers**: Set to number of CPU cores for optimal performance

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon PostgreSQL Documentation](https://neon.tech/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [python-jose Documentation](https://python-jose.readthedocs.io/)
- [JWT.io Token Decoder](https://jwt.io/)

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the API documentation at `/docs`
3. Check the project specification in `specs/002-backend-jwt-auth/`

---

**Status**: Production Ready with JWT Authentication
**Version**: 1.0.0
**Last Updated**: 2026-02-05
