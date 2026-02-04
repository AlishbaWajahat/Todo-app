# Authentication Flow Testing Guide

**Feature**: Backend JWT Authentication & API Security
**Date**: 2026-02-05
**Purpose**: End-to-end testing instructions and verification checklist

## Overview

This guide provides step-by-step instructions for testing the complete authentication flow, including JWT token generation, user provisioning, and user isolation verification.

## Prerequisites

- Backend server running: `uvicorn main:app --reload`
- Database migrations applied: `alembic upgrade head`
- Environment variables configured in `.env`
- Better Auth frontend (or JWT token generator)

## Quick Test with Swagger UI

1. **Start the server**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Open Swagger UI**
   - Navigate to http://localhost:8000/docs

3. **Generate a test JWT token** (Python script):
   ```python
   from jose import jwt
   from datetime import datetime, timedelta
   
   SECRET = "your-jwt-secret-from-env"  # Must match .env
   payload = {
       "sub": "test_user_123",
       "email": "test@example.com",
       "name": "Test User",
       "exp": datetime.utcnow() + timedelta(hours=1)
   }
   token = jwt.encode(payload, SECRET, algorithm="HS256")
   print(token)
   ```

4. **Authorize in Swagger**
   - Click "Authorize" button
   - Enter: `Bearer <your-token>`
   - Click "Authorize" then "Close"

5. **Test endpoints**
   - Try GET /api/v1/tasks (should return empty array)
   - Try POST /api/v1/tasks (create a task)
   - Try GET /api/v1/tasks again (should show your task)

## Test Checklist

### Authentication Tests
- [ ] Missing token returns 401
- [ ] Invalid token returns 401
- [ ] Expired token returns 401
- [ ] Valid token allows access

### User Provisioning Tests
- [ ] First authentication creates user in database
- [ ] Subsequent authentications reuse existing user
- [ ] User data matches JWT claims (id, email, name)

### CRUD Tests
- [ ] Create task returns 201 with Location header
- [ ] List tasks returns only user's tasks
- [ ] Get task by ID works for owned tasks
- [ ] Update task works for owned tasks
- [ ] Delete task works for owned tasks

### User Isolation Tests
- [ ] User A cannot access User B's tasks (404)
- [ ] User A cannot update User B's tasks (404)
- [ ] User A cannot delete User B's tasks (404)
- [ ] List tasks shows only own tasks

### Error Handling Tests
- [ ] Invalid request body returns 422
- [ ] Missing required fields returns 422
- [ ] Server errors return 500 with generic message

## Manual Testing Commands

### Test Authentication

```bash
# Missing token (should return 401)
curl http://localhost:8000/api/v1/tasks

# Invalid token (should return 401)
curl -H "Authorization: Bearer invalid" http://localhost:8000/api/v1/tasks

# Valid token (should return 200)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/tasks
```

### Test CRUD Operations

```bash
# Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"Testing"}'

# List tasks
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/tasks

# Get task by ID
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/tasks/1

# Update task
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# Delete task
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer <token>"
```

### Test User Isolation

```bash
# Generate two different user tokens
# Token 1: user_id = "user_a"
# Token 2: user_id = "user_b"

# Create task with User A token
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <user-a-token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"User A Task"}'

# Try to access with User B token (should return 404)
curl -H "Authorization: Bearer <user-b-token>" \
  http://localhost:8000/api/v1/tasks/1
```

## Database Verification

```sql
-- Check users table
SELECT * FROM users;

-- Check tasks table with user info
SELECT t.*, u.email FROM tasks t JOIN users u ON t.user_id = u.id;

-- Verify user isolation (should return 0)
SELECT COUNT(*) FROM tasks t1, tasks t2 
WHERE t1.id = t2.id AND t1.user_id != t2.user_id;
```

## Expected Results

All tests should pass with:
- ✅ Proper authentication enforcement
- ✅ Automatic user provisioning
- ✅ Strict user isolation
- ✅ Consistent error responses
- ✅ RESTful API behavior

---

**Status**: Ready for integration testing
**Next Step**: Integrate with Better Auth frontend
