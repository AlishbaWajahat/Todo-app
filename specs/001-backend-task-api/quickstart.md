# Quickstart Guide

**Feature**: Backend Core – Task API & Database Layer
**Date**: 2026-02-03
**Phase**: Phase 1 - Design

## Overview

This guide provides step-by-step instructions for setting up and running the Task Management API locally. Follow these instructions to get the backend service running and start testing the API endpoints.

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Python package installer (included with Python)
- **Neon PostgreSQL Database**: [Sign up for Neon](https://neon.tech/) (free tier available)
- **Git**: For cloning the repository

---

## Step 1: Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Switch to the feature branch
git checkout 001-backend-task-api
```

---

## Step 2: Set Up Python Environment

### Option A: Using venv (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Option B: Using conda

```bash
# Create conda environment
conda create -n task-api python=3.11
conda activate task-api
```

---

## Step 3: Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install required packages
pip install -r requirements.txt
```

**Expected packages**:
- fastapi
- sqlmodel
- uvicorn[standard]
- psycopg2-binary
- python-dotenv
- pydantic-settings

---

## Step 4: Configure Environment Variables

### Create .env file

```bash
# Copy the example environment file
cp .env.example .env
```

### Edit .env file

Open `.env` in your text editor and add your Neon database connection string:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# CORS Configuration (for frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Get Neon Database URL

1. Log in to [Neon Console](https://console.neon.tech/)
2. Select your project (or create a new one)
3. Go to "Connection Details"
4. Copy the connection string (format: `postgresql://user:password@host/database`)
5. Paste it into your `.env` file as `DATABASE_URL`

**Important**: Ensure `?sslmode=require` is appended to the connection string for secure connections.

---

## Step 5: Verify Configuration

```bash
# Test that environment variables are loaded correctly
python -c "from core.config import settings; print(settings.database_url)"
```

**Expected output**: Your database URL (with password masked)

---

## Step 6: Initialize Database

The database tables will be created automatically when you first run the application.

**Manual initialization** (optional):

```python
# Run this in Python shell if you want to create tables manually
from core.database import engine
from sqlmodel import SQLModel
from models.task import Task

SQLModel.metadata.create_all(engine)
print("Database tables created successfully!")
```

---

## Step 7: Run the Server

### Development Mode (with auto-reload)

```bash
# From backend/ directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Production Mode (no auto-reload)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Step 8: Verify API is Running

### Check Health Endpoint

```bash
# Using curl
curl http://localhost:8000/

# Expected response:
# {"message": "Task Management API"}
```

### Access API Documentation

Open your browser and navigate to:

**Interactive API Docs (Swagger UI)**:
- URL: http://localhost:8000/docs
- Features: Try out endpoints, see request/response schemas

**Alternative API Docs (ReDoc)**:
- URL: http://localhost:8000/redoc
- Features: Clean documentation view

---

## Step 9: Test API Endpoints

### Using FastAPI Docs (Recommended)

1. Open http://localhost:8000/docs
2. Click on any endpoint (e.g., "POST /api/v1/tasks")
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"
6. View the response

### Using curl

**Create a task**:
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task",
    "description": "This is a test task",
    "completed": false,
    "user_id": 1
  }'
```

**List all tasks**:
```bash
curl http://localhost:8000/api/v1/tasks
```

**Get a specific task**:
```bash
curl http://localhost:8000/api/v1/tasks/1
```

**Update a task**:
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated task",
    "description": "Updated description",
    "completed": true,
    "user_id": 1
  }'
```

**Partially update a task (toggle completed)**:
```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Delete a task**:
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/1
```

### Using Postman

1. Import the OpenAPI spec from `specs/001-backend-task-api/contracts/openapi.yaml`
2. Set base URL to `http://localhost:8000`
3. Test each endpoint

---

## Common Issues & Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue 2: "Could not connect to database"

**Solution**: Verify DATABASE_URL in .env file
```bash
# Check if .env file exists
cat .env

# Verify connection string format
# Should be: postgresql://user:password@host/database?sslmode=require
```

### Issue 3: "Port 8000 already in use"

**Solution**: Use a different port
```bash
uvicorn main:app --reload --port 8001
```

### Issue 4: "CORS error when calling from frontend"

**Solution**: Add frontend origin to CORS_ORIGINS in .env
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Issue 5: "Table 'task' does not exist"

**Solution**: Restart the server to trigger table creation
```bash
# Stop server (CTRL+C)
# Start server again
uvicorn main:app --reload
```

---

## Development Workflow

### Making Changes

1. **Modify code** in your editor
2. **Save the file** - server auto-reloads (if using --reload flag)
3. **Test changes** in browser at http://localhost:8000/docs
4. **Verify** response format and status codes

### Testing Database Persistence

1. Create a task via API
2. Stop the server (CTRL+C)
3. Start the server again
4. List tasks - the created task should still exist

### Viewing Logs

Server logs appear in the terminal where you ran `uvicorn`. Look for:
- SQL queries (if echo=True in database config)
- HTTP requests and responses
- Error messages and stack traces

---

## Next Steps

### After Setup

1. ✅ Verify all 6 endpoints work correctly
2. ✅ Test error cases (missing fields, invalid IDs)
3. ✅ Verify database persistence
4. ✅ Check CORS configuration for frontend integration

### Future Enhancements

- Add JWT authentication middleware
- Implement pagination for task listing
- Add filtering and sorting capabilities
- Set up automated tests
- Configure CI/CD pipeline

---

## API Endpoint Summary

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| GET | `/api/v1/tasks` | List all tasks | 200, 500 |
| POST | `/api/v1/tasks` | Create a task | 201, 400, 500 |
| GET | `/api/v1/tasks/{id}` | Get task by ID | 200, 404, 500 |
| PUT | `/api/v1/tasks/{id}` | Update task (full) | 200, 400, 404, 500 |
| PATCH | `/api/v1/tasks/{id}` | Update task (partial) | 200, 400, 404, 500 |
| DELETE | `/api/v1/tasks/{id}` | Delete task | 204, 404, 500 |

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | None | Neon PostgreSQL connection string |
| `CORS_ORIGINS` | No | `["http://localhost:3000"]` | Allowed CORS origins (comma-separated) |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |

---

## Useful Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server with auto-reload
uvicorn main:app --reload

# Run server on different port
uvicorn main:app --reload --port 8001

# Check Python version
python --version

# List installed packages
pip list

# Freeze dependencies
pip freeze > requirements.txt

# Deactivate virtual environment
deactivate
```

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Neon Documentation**: https://neon.tech/docs/
- **OpenAPI Specification**: See `specs/001-backend-task-api/contracts/openapi.yaml`
- **Data Model**: See `specs/001-backend-task-api/data-model.md`

---

## Support

If you encounter issues not covered in this guide:

1. Check the [research.md](./research.md) for technical decisions and rationale
2. Review the [plan.md](./plan.md) for implementation details
3. Consult the [data-model.md](./data-model.md) for entity definitions
4. Check FastAPI logs for error messages

---

## Success Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] .env file created with DATABASE_URL
- [ ] Neon database connection verified
- [ ] Server running on http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] All 6 endpoints tested and working
- [ ] Database persistence verified
- [ ] CORS configured for frontend

**When all items are checked, you're ready to proceed with frontend integration!**
