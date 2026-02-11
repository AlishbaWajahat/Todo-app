# API Integration Contracts

**Feature**: 003-frontend-todo-ui
**Date**: 2026-02-06
**Purpose**: Document backend API endpoints and integration patterns for frontend consumption

---

## Overview

This document defines the contract between the frontend (Next.js) and backend (FastAPI) applications. All API endpoints require JWT authentication except where explicitly noted.

**Base URL**: `http://localhost:8000` (development) or configured via `NEXT_PUBLIC_API_URL`

**Authentication**: All protected endpoints require `Authorization: Bearer <jwt_token>` header

**Response Format**: All responses return JSON with consistent structure

---

## Authentication Endpoints

### Sign Up

Create a new user account.

**Endpoint**: `POST /api/v1/auth/signup`

**Authentication**: Not required (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Success Response** (201 Created):
```json
{
  "user": {
    "id": "user_123abc",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar_url": null,
    "created_at": "2026-02-06T10:30:00Z",
    "updated_at": "2026-02-06T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:
- 400 Bad Request: Invalid input
  ```json
  {
    "detail": "Email already registered",
    "code": "EMAIL_EXISTS"
  }
  ```
- 422 Unprocessable Entity: Validation error
  ```json
  {
    "detail": "Password must be at least 8 characters",
    "code": "VALIDATION_ERROR",
    "field": "password"
  }
  ```

---

### Sign In

Authenticate user and receive JWT token.

**Endpoint**: `POST /api/v1/auth/signin`

**Authentication**: Not required (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response** (200 OK):
```json
{
  "user": {
    "id": "user_123abc",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar_url": "https://example.com/avatars/user_123abc.jpg",
    "created_at": "2026-02-06T10:30:00Z",
    "updated_at": "2026-02-06T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:
- 401 Unauthorized: Invalid credentials
  ```json
  {
    "detail": "Invalid email or password",
    "code": "INVALID_CREDENTIALS"
  }
  ```

---

## Task Endpoints

### List Tasks

Get all tasks for the authenticated user.

**Endpoint**: `GET /api/v1/tasks`

**Authentication**: Required

**Query Parameters**:
- `completed` (optional): Filter by completion status (true/false)
- `priority` (optional): Filter by priority (low/medium/high)
- `skip` (optional): Number of tasks to skip (pagination, default: 0)
- `limit` (optional): Maximum tasks to return (pagination, default: 100)

**Example Request**:
```
GET /api/v1/tasks?completed=false&priority=high
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": "user_123abc",
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "completed": false,
    "priority": "high",
    "due_date": "2026-02-10T00:00:00Z",
    "created_at": "2026-02-06T10:30:00Z",
    "updated_at": "2026-02-06T10:30:00Z"
  },
  {
    "id": 2,
    "user_id": "user_123abc",
    "title": "Review pull requests",
    "description": null,
    "completed": false,
    "priority": "medium",
    "due_date": null,
    "created_at": "2026-02-06T11:00:00Z",
    "updated_at": "2026-02-06T11:00:00Z"
  }
]
```

**Error Responses**:
- 401 Unauthorized: Missing or invalid token
  ```json
  {
    "detail": "Authentication required",
    "code": "UNAUTHORIZED"
  }
  ```

---

### Get Single Task

Get a specific task by ID.

**Endpoint**: `GET /api/v1/tasks/{task_id}`

**Authentication**: Required

**Path Parameters**:
- `task_id`: Task ID (integer)

**Example Request**:
```
GET /api/v1/tasks/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": "user_123abc",
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "completed": false,
  "priority": "high",
  "due_date": "2026-02-10T00:00:00Z",
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T10:30:00Z"
}
```

**Error Responses**:
- 404 Not Found: Task doesn't exist or doesn't belong to user
  ```json
  {
    "detail": "Task not found or you don't have permission to access it",
    "code": "TASK_NOT_FOUND"
  }
  ```

---

### Create Task

Create a new task.

**Endpoint**: `POST /api/v1/tasks`

**Authentication**: Required

**Request Body**:
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "priority": "high",
  "due_date": "2026-02-10T00:00:00Z"
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "user_id": "user_123abc",
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "completed": false,
  "priority": "high",
  "due_date": "2026-02-10T00:00:00Z",
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T10:30:00Z"
}
```

**Response Headers**:
- `Location: /api/v1/tasks/1`

**Error Responses**:
- 400 Bad Request: Invalid input
  ```json
  {
    "detail": "Title is required",
    "code": "VALIDATION_ERROR",
    "field": "title"
  }
  ```

---

### Update Task

Update an existing task.

**Endpoint**: `PUT /api/v1/tasks/{task_id}`

**Authentication**: Required

**Path Parameters**:
- `task_id`: Task ID (integer)

**Request Body** (all fields optional):
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "completed": true,
  "priority": "medium",
  "due_date": "2026-02-15T00:00:00Z"
}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": "user_123abc",
  "title": "Updated task title",
  "description": "Updated description",
  "completed": true,
  "priority": "medium",
  "due_date": "2026-02-15T00:00:00Z",
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T15:45:00Z"
}
```

**Error Responses**:
- 404 Not Found: Task doesn't exist or doesn't belong to user
  ```json
  {
    "detail": "Task not found or you don't have permission to access it",
    "code": "TASK_NOT_FOUND"
  }
  ```

---

### Delete Task

Delete a task.

**Endpoint**: `DELETE /api/v1/tasks/{task_id}`

**Authentication**: Required

**Path Parameters**:
- `task_id`: Task ID (integer)

**Example Request**:
```
DELETE /api/v1/tasks/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response** (204 No Content):
```
(empty response body)
```

**Error Responses**:
- 404 Not Found: Task doesn't exist or doesn't belong to user
  ```json
  {
    "detail": "Task not found or you don't have permission to access it",
    "code": "TASK_NOT_FOUND"
  }
  ```

---

## User Profile Endpoints

### Get Current User

Get the authenticated user's profile.

**Endpoint**: `GET /api/v1/users/me`

**Authentication**: Required

**Example Request**:
```
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response** (200 OK):
```json
{
  "id": "user_123abc",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar_url": "https://example.com/avatars/user_123abc.jpg",
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T10:30:00Z"
}
```

---

### Update Profile

Update the authenticated user's profile.

**Endpoint**: `PUT /api/v1/users/me`

**Authentication**: Required

**Request Body**:
```json
{
  "name": "Jane Doe"
}
```

**Success Response** (200 OK):
```json
{
  "id": "user_123abc",
  "email": "user@example.com",
  "name": "Jane Doe",
  "avatar_url": "https://example.com/avatars/user_123abc.jpg",
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T16:00:00Z"
}
```

---

### Upload Avatar

Upload a new profile picture.

**Endpoint**: `POST /api/v1/users/me/avatar`

**Authentication**: Required

**Request Body**: `multipart/form-data`
- `avatar`: Image file (JPEG, PNG, GIF, max 5MB)

**Example Request**:
```
POST /api/v1/users/me/avatar
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data

------WebKitFormBoundary
Content-Disposition: form-data; name="avatar"; filename="profile.jpg"
Content-Type: image/jpeg

[binary image data]
------WebKitFormBoundary--
```

**Success Response** (200 OK):
```json
{
  "id": "user_123abc",
  "email": "user@example.com",
  "name": "Jane Doe",
  "avatar_url": "https://example.com/avatars/user_123abc_new.jpg",
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T16:30:00Z"
}
```

**Error Responses**:
- 400 Bad Request: Invalid file
  ```json
  {
    "detail": "File size exceeds 5MB limit",
    "code": "FILE_TOO_LARGE"
  }
  ```

---

## Error Response Format

All error responses follow this consistent format:

```json
{
  "detail": "Human-readable error message",
  "code": "MACHINE_READABLE_ERROR_CODE",
  "field": "field_name"  // Optional, for validation errors
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Authentication required or token invalid |
| `FORBIDDEN` | 403 | Access denied |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `TASK_NOT_FOUND` | 404 | Specific task not found |
| `USER_NOT_FOUND` | 404 | Specific user not found |
| `EMAIL_EXISTS` | 400 | Email already registered |
| `INVALID_CREDENTIALS` | 401 | Invalid email or password |
| `FILE_TOO_LARGE` | 400 | Uploaded file exceeds size limit |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Frontend Integration Patterns

### API Client Setup

```typescript
// lib/api/client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const session = await auth.api.getSession();

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session?.session?.token}`,
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new ApiError(error.detail, error.code, response.status);
  }

  return response.json();
}
```

### Usage Examples

**List Tasks**:
```typescript
const tasks = await apiRequest<Task[]>('/api/v1/tasks');
```

**Create Task**:
```typescript
const newTask = await apiRequest<Task>('/api/v1/tasks', {
  method: 'POST',
  body: JSON.stringify({
    title: 'New task',
    priority: 'high',
  }),
});
```

**Update Task**:
```typescript
const updatedTask = await apiRequest<Task>(`/api/v1/tasks/${taskId}`, {
  method: 'PUT',
  body: JSON.stringify({
    completed: true,
  }),
});
```

**Delete Task**:
```typescript
await apiRequest<void>(`/api/v1/tasks/${taskId}`, {
  method: 'DELETE',
});
```

---

## CORS Configuration

The backend must be configured to allow requests from the frontend origin:

**Backend CORS Settings** (already configured in Feature 002):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Frontend Configuration**:
- Set `NEXT_PUBLIC_API_URL` environment variable
- Ensure credentials are included in requests
- Handle CORS preflight requests (OPTIONS)

---

## Rate Limiting

The backend may implement rate limiting (future enhancement):
- Authentication endpoints: 10 requests/minute per IP
- Read endpoints (GET): 100 requests/minute per user
- Write endpoints (POST/PUT/DELETE): 30 requests/minute per user

**Rate Limit Headers** (if implemented):
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1675689600
```

---

## Testing the API

### Using cURL

**Sign Up**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'
```

**Sign In**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**List Tasks** (with token):
```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Create Task**:
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","priority":"high"}'
```

### Using FastAPI Docs

The backend provides interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Summary

This API contract provides:
- **Consistent Structure**: All endpoints follow RESTful conventions
- **Type Safety**: Clear request/response schemas
- **Error Handling**: Consistent error format with codes
- **Authentication**: JWT-based security on all protected endpoints
- **Documentation**: Comprehensive examples and usage patterns

**Next Steps**: Implement frontend API client using these contracts.
