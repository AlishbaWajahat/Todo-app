# Data Model: Backend JWT Authentication & API Security

**Feature**: Backend JWT Authentication & API Security
**Date**: 2026-02-05
**Purpose**: Define database schema and entity relationships

## Entity Overview

This feature introduces the `User` entity and updates the existing `Task` entity to support multi-user functionality with strict user isolation.

## Entities

### User

**Purpose**: Represents an authenticated user in the system. Automatically provisioned from JWT token data on first authentication.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | String (VARCHAR) | PRIMARY KEY, NOT NULL | User ID from JWT "sub" claim (e.g., UUID or auth provider ID) |
| email | String (VARCHAR) | UNIQUE, NOT NULL | User email address from JWT "email" claim |
| name | String (VARCHAR) | NULLABLE | User display name from JWT "name" claim |
| avatar_url | String (VARCHAR) | NULLABLE | User profile picture URL (reserved for future use) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Timestamp when user record was created |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Timestamp when user record was last updated |

**Indexes**:
- PRIMARY KEY on `id` (automatic)
- UNIQUE INDEX on `email` (prevents duplicate emails)

**Validation Rules**:
- `id` must be non-empty string (validated at application level)
- `email` must be valid email format (validated by Pydantic EmailStr)
- `name` can be null (some JWT tokens may not include name)
- `avatar_url` must be valid URL if provided (validated by Pydantic HttpUrl)

**Relationships**:
- One-to-Many with Task (one user has many tasks)

**State Transitions**: None (user records are immutable after creation, except for future profile update features)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)  # From JWT "sub" claim
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### Task (Updated)

**Purpose**: Represents a todo item belonging to a specific user. Updated to include user_id foreign key for multi-user support.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO INCREMENT | Unique task identifier |
| user_id | String (VARCHAR) | FOREIGN KEY (users.id), NOT NULL, INDEX | Owner of this task |
| title | String (VARCHAR) | NOT NULL | Task title/description |
| description | String (TEXT) | NULLABLE | Detailed task description |
| completed | Boolean | NOT NULL, DEFAULT FALSE | Task completion status |
| priority | String (VARCHAR) | NULLABLE | Task priority (low, medium, high) |
| due_date | DateTime | NULLABLE | Task due date |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Timestamp when task was created |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Timestamp when task was last updated |

**Indexes**:
- PRIMARY KEY on `id` (automatic)
- INDEX on `user_id` (for fast user-scoped queries)
- COMPOSITE INDEX on `(id, user_id)` (for single-task lookups with user validation)

**Validation Rules**:
- `title` must be non-empty string (1-200 characters)
- `description` can be null or up to 2000 characters
- `completed` defaults to false
- `priority` must be one of: "low", "medium", "high", or null
- `due_date` must be future date if provided
- `user_id` must reference existing user in users table

**Relationships**:
- Many-to-One with User (many tasks belong to one user)

**State Transitions**:
- Created → Incomplete (completed=false)
- Incomplete → Completed (completed=true)
- Completed → Incomplete (completed=false) - can be toggled

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)  # NEW FIELD
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship (optional, for future use)
    # user: Optional[User] = Relationship(back_populates="tasks")
```

---

## Entity Relationships

```
User (1) ──────< (Many) Task
  │                      │
  └─ id                  └─ user_id (FK)
```

**Relationship Rules**:
- One user can have many tasks (0 to unlimited)
- Each task belongs to exactly one user (required)
- Deleting a user should cascade delete all their tasks (ON DELETE CASCADE)
- User cannot be deleted if they have tasks (application-level constraint, optional)

---

## Database Migration Strategy

### Migration 1: Create Users Table

**File**: `alembic/versions/[timestamp]_create_users_table.py`

**Up**:
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    avatar_url VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**Down**:
```sql
DROP INDEX idx_users_email;
DROP TABLE users;
```

---

### Migration 2: Add user_id to Tasks Table

**File**: `alembic/versions/[timestamp]_add_user_id_to_tasks.py`

**Up**:
```sql
-- Add user_id column (nullable initially for existing data)
ALTER TABLE tasks ADD COLUMN user_id VARCHAR;

-- Add foreign key constraint
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_user_id
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Create index for fast user-scoped queries
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Create composite index for single-task lookups with user validation
CREATE INDEX idx_tasks_id_user_id ON tasks(id, user_id);

-- Make user_id NOT NULL (after backfilling existing data if needed)
-- ALTER TABLE tasks ALTER COLUMN user_id SET NOT NULL;
```

**Down**:
```sql
DROP INDEX idx_tasks_id_user_id;
DROP INDEX idx_tasks_user_id;
ALTER TABLE tasks DROP CONSTRAINT fk_tasks_user_id;
ALTER TABLE tasks DROP COLUMN user_id;
```

**Note**: If existing tasks exist in the database, a data migration step is needed to assign them to a default user before making user_id NOT NULL. For a fresh database (hackathon MVP), this is not necessary.

---

## Query Patterns

### User Provisioning (Idempotent)

```python
from sqlalchemy.exc import IntegrityError

def get_or_create_user(session: Session, user_id: str, email: str, name: Optional[str]) -> User:
    """
    Get existing user or create new one (idempotent, handles race conditions).
    """
    # Try to fetch existing user
    user = session.get(User, user_id)
    if user:
        return user

    # User doesn't exist, create new one
    try:
        user = User(id=user_id, email=email, name=name)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError:
        # Race condition: another request created the user
        session.rollback()
        user = session.get(User, user_id)
        return user
```

### User-Scoped Task Queries

```python
from sqlmodel import select

# Get all tasks for a user
def get_user_tasks(session: Session, user_id: str) -> list[Task]:
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()

# Get specific task for a user (returns None if not found or wrong user)
def get_user_task(session: Session, task_id: int, user_id: str) -> Optional[Task]:
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    return session.exec(statement).first()

# Create task for a user
def create_task(session: Session, user_id: str, title: str, **kwargs) -> Task:
    task = Task(user_id=user_id, title=title, **kwargs)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# Update task (only if owned by user)
def update_task(session: Session, task_id: int, user_id: str, **updates) -> Optional[Task]:
    task = get_user_task(session, task_id, user_id)
    if not task:
        return None

    for key, value in updates.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)
    return task

# Delete task (only if owned by user)
def delete_task(session: Session, task_id: int, user_id: str) -> bool:
    task = get_user_task(session, task_id, user_id)
    if not task:
        return False

    session.delete(task)
    session.commit()
    return True
```

---

## Performance Considerations

**Index Strategy**:
- `users.id` (PRIMARY KEY): O(1) lookup for user provisioning
- `users.email` (UNIQUE INDEX): O(log n) lookup for email-based queries (future feature)
- `tasks.user_id` (INDEX): O(log n) filtering for user-scoped task lists
- `tasks.(id, user_id)` (COMPOSITE INDEX): O(log n) lookup for single-task validation

**Expected Query Performance**:
- User provisioning: <5ms (primary key lookup or insert)
- Get all user tasks: <10ms for typical user (<1000 tasks)
- Get single task: <5ms (composite index lookup)
- Create task: <10ms (insert + index updates)
- Update task: <10ms (lookup + update)
- Delete task: <10ms (lookup + delete)

**Scalability**:
- Users table: Supports millions of users (primary key index)
- Tasks table: Supports millions of tasks (user_id index ensures fast filtering)
- No N+1 query issues (no relationship loading in this feature)

---

## Data Integrity

**Constraints**:
- `users.id` PRIMARY KEY ensures unique user IDs
- `users.email` UNIQUE ensures no duplicate emails
- `tasks.user_id` FOREIGN KEY ensures referential integrity
- `tasks.user_id` NOT NULL ensures every task has an owner

**Cascade Behavior**:
- ON DELETE CASCADE: Deleting a user deletes all their tasks
- ON UPDATE CASCADE: Not needed (user IDs are immutable)

**Application-Level Validation**:
- Email format validation (Pydantic EmailStr)
- Task title length validation (1-200 characters)
- Task priority enum validation (low, medium, high)
- Due date future validation (if provided)

---

## Security Considerations

**User Isolation**:
- All task queries MUST include `WHERE user_id = <authenticated_user_id>`
- No global task queries allowed (would leak cross-user data)
- 404 Not Found returned for wrong user (prevents information leakage)

**Data Exposure**:
- User email is sensitive (only exposed to authenticated user)
- Task data is private (only accessible to owner)
- No public endpoints (all require authentication)

**Audit Trail**:
- `created_at` and `updated_at` timestamps for all entities
- Authentication failures logged (not stored in database)
- User provisioning events logged (not stored in database)
