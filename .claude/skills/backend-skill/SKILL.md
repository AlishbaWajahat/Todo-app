---
name: backend-routing-db
description: Build FastAPI backend with SQLModel ORM, RESTful routes, request validation, and Neon PostgreSQL integration.
---

# FastAPI Backend with SQLModel & Neon PostgreSQL

**Tech Stack:** Python FastAPI + SQLModel + Neon Serverless PostgreSQL

## Instructions

1. **Project setup**
   - Initialize FastAPI application
   - Configure environment variables (.env file)
   - Setup folder structure (api/routes, models, schemas, core, services)
   - Install dependencies: fastapi, sqlmodel, psycopg2-binary, python-jose, uvicorn

2. **SQLModel Models & Database**
   - Define SQLModel models with `table=True` for database tables
   - Create separate request/response schemas
   - Configure Neon PostgreSQL connection with connection pooling
   - Use SQLModel's `create_engine` with proper connection string
   - Implement database session dependency

3. **FastAPI Routing**
   - Create RESTful routes (GET, POST, PUT, PATCH, DELETE)
   - Use APIRouter for route organization
   - Implement path parameters and query parameters
   - Use Pydantic models for request/response validation
   - Add proper HTTP status codes

4. **Request & Response Handling**
   - Use Pydantic/SQLModel for automatic validation
   - Return SQLModel instances or Pydantic schemas
   - Handle validation errors with proper error messages
   - Use proper HTTP status codes (200, 201, 204, 400, 404, 500)
   - Implement consistent response structure

5. **Database Operations**
   - Use SQLModel Session for database operations
   - Implement CRUD operations with type safety
   - Use `select()` for queries
   - Handle transactions with session context managers
   - Implement proper error handling for database operations

6. **Error Handling & Middleware**
   - Use FastAPI's HTTPException for errors
   - Implement custom exception handlers
   - Add CORS middleware for frontend communication
   - Add logging middleware
   - Implement authentication middleware (JWT verification)

## Best Practices
- Follow RESTful API conventions
- Use async/await for I/O operations
- Keep route handlers thin, move logic to services
- Use dependency injection for database sessions
- Validate all inputs with Pydantic/SQLModel
- Use environment variables for secrets (DATABASE_URL, JWT_SECRET)
- Return consistent API response structure
- Implement proper error handling with meaningful messages
- Use type hints throughout
- Configure connection pooling for Neon serverless

## Example Structure

```python
# models/user.py
from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    created_at: Optional[str] = None

class UserCreate(SQLModel):
    email: str
    name: str

class UserResponse(SQLModel):
    id: int
    email: str
    name: str

# core/database.py
from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

# api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.user import User, UserCreate, UserResponse
from core.database import get_session

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserResponse])
async def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    user = User.model_validate(user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import users

app = FastAPI(title="Todo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Todo API"}
```

## Neon PostgreSQL Configuration

```python
# .env
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/dbname?sslmode=require

# Connection pooling for serverless
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10
)
```
