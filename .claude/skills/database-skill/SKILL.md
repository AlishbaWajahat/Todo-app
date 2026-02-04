---
name: database-design
description: Design scalable databases with SQLModel ORM, Neon PostgreSQL, proper schema, migrations, and serverless optimization.
---

# Database Design with SQLModel & Neon PostgreSQL

**Tech Stack:** Neon Serverless PostgreSQL + SQLModel + Alembic (migrations)

## Instructions

1. **SQLModel Schema Design**
   - Define SQLModel classes with `table=True` for database tables
   - Use proper type hints (int, str, Optional, etc.)
   - Define primary keys with `Field(default=None, primary_key=True)`
   - Add foreign keys with `Field(foreign_key="table.column")`
   - Use `Field()` for constraints (unique, index, nullable)
   - Create separate request/response models without `table=True`

2. **Table Design Best Practices**
   - Normalize tables to reduce redundancy (3NF)
   - Use appropriate data types (int, str, bool, datetime)
   - Add indexes on foreign keys and frequently queried columns
   - Implement proper primary and foreign key relationships
   - Use meaningful, consistent naming conventions (snake_case)
   - Add timestamps (created_at, updated_at) where needed

3. **Relationships & Foreign Keys**
   - Define foreign key relationships between tables
   - Use proper cascade rules (CASCADE, SET NULL, RESTRICT)
   - Ensure referential integrity with constraints
   - Consider one-to-many and many-to-many relationships
   - Use SQLModel's relationship features when needed

4. **Database Migrations (Alembic)**
   - Initialize Alembic for migration management
   - Generate migrations from SQLModel changes
   - Write reversible migrations (upgrade/downgrade)
   - Test migrations on development database first
   - Never edit old migrations; create new ones
   - Version control all migration files

5. **Neon Serverless Optimization**
   - Configure connection pooling (PgBouncer recommended)
   - Use `pool_pre_ping=True` to verify connections
   - Set appropriate pool_size and max_overflow
   - Handle cold starts gracefully
   - Leverage Neon branching for development/testing
   - Use Neon's auto-scaling features

6. **Constraints & Data Integrity**
   - Add NOT NULL constraints where appropriate
   - Use UNIQUE constraints for unique fields (email, username)
   - Implement CHECK constraints for validation
   - Add DEFAULT values where sensible
   - Use foreign key constraints for relationships
   - Implement proper cascading behavior

## Best Practices
- Design schema before writing code
- Use SQLModel for type-safe database operations
- Keep tables focused and normalized
- Add indexes strategically (not on every column)
- Use migrations for all schema changes
- Test migrations thoroughly before production
- Configure connection pooling for serverless
- Use environment variables for database credentials
- Implement proper error handling for database operations
- Monitor query performance with EXPLAIN ANALYZE

## Example Structure

### SQLModel Models

```python
# models/user.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    """User table - stores user accounts"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=100)
    password_hash: str = Field(max_length=255)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

class UserCreate(SQLModel):
    """Request model for creating users"""
    email: str
    name: str
    password: str

class UserResponse(SQLModel):
    """Response model for user data (no password)"""
    id: int
    email: str
    name: str
    created_at: datetime
    is_active: bool

# models/todo.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Todo(SQLModel, table=True):
    """Todo table - stores user todos"""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class TodoCreate(SQLModel):
    """Request model for creating todos"""
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoUpdate(SQLModel):
    """Request model for updating todos"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(SQLModel):
    """Response model for todo data"""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    user_id: int
    created_at: datetime
    updated_at: datetime
```

### Database Connection & Engine

```python
# core/database.py
from sqlmodel import create_engine, Session, SQLModel
import os

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with connection pooling for Neon serverless
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Additional connections when pool is full
    pool_recycle=3600,  # Recycle connections after 1 hour
)

def create_db_and_tables():
    """Create all tables defined in SQLModel"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session
```

### Database Migrations with Alembic

```bash
# Initialize Alembic
alembic init alembic

# Generate migration from SQLModel changes
alembic revision --autogenerate -m "Create users and todos tables"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

```python
# alembic/env.py - Configure Alembic with SQLModel
from sqlmodel import SQLModel
from models.user import User
from models.todo import Todo

# Import all models so Alembic can detect them
target_metadata = SQLModel.metadata

# ... rest of Alembic configuration
```

### Example Migration File

```python
# alembic/versions/xxx_create_users_and_todos.py
"""Create users and todos tables

Revision ID: xxx
Revises:
Create Date: 2024-01-01 12:00:00
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision = 'xxx'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_user_email', 'user', ['email'])

    # Create todos table
    op.create_table(
        'todo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_todo_user_id', 'todo', ['user_id'])

def downgrade() -> None:
    op.drop_index('ix_todo_user_id', table_name='todo')
    op.drop_table('todo')
    op.drop_index('ix_user_email', table_name='user')
    op.drop_table('user')
```

### CRUD Operations with SQLModel

```python
# Example CRUD operations
from sqlmodel import Session, select
from models.todo import Todo, TodoCreate, TodoUpdate

# CREATE
def create_todo(session: Session, todo_data: TodoCreate, user_id: int) -> Todo:
    todo = Todo(**todo_data.model_dump(), user_id=user_id)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

# READ (single)
def get_todo(session: Session, todo_id: int) -> Todo | None:
    return session.get(Todo, todo_id)

# READ (multiple with filter)
def get_user_todos(session: Session, user_id: int) -> list[Todo]:
    statement = select(Todo).where(Todo.user_id == user_id)
    return session.exec(statement).all()

# UPDATE
def update_todo(session: Session, todo_id: int, todo_data: TodoUpdate) -> Todo:
    todo = session.get(Todo, todo_id)
    if not todo:
        raise ValueError("Todo not found")

    # Update only provided fields
    for key, value in todo_data.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

# DELETE
def delete_todo(session: Session, todo_id: int) -> None:
    todo = session.get(Todo, todo_id)
    if todo:
        session.delete(todo)
        session.commit()
```

## Neon PostgreSQL Configuration

```bash
# .env
DATABASE_URL=postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# Connection string format for Neon
# postgresql://[user]:[password]@[endpoint]/[database]?sslmode=require
```

## Schema Design Checklist
- [ ] All tables have primary keys
- [ ] Foreign keys defined for relationships
- [ ] Indexes added on foreign keys and frequently queried columns
- [ ] Unique constraints on unique fields (email, username)
- [ ] NOT NULL constraints where appropriate
- [ ] Default values set where sensible
- [ ] Timestamps (created_at, updated_at) included
- [ ] Proper data types chosen (not over-sized)
- [ ] Tables normalized to reduce redundancy
- [ ] Cascade rules defined for foreign keys
- [ ] SQLModel models match database schema
- [ ] Migrations created for all schema changes
- [ ] Connection pooling configured for serverless
