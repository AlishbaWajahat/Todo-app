# Data Model: Frontend UI & Profile Integration

**Feature**: 003-frontend-todo-ui
**Date**: 2026-02-06
**Purpose**: Define TypeScript interfaces and data structures for the frontend application

---

## Overview

This document defines all TypeScript interfaces, types, and data structures used in the frontend application. These types ensure type safety across components, API calls, and state management.

---

## Core Entities

### User

Represents an authenticated user in the system.

```typescript
export interface User {
  id: string;                    // Unique user identifier (from JWT "sub" claim)
  email: string;                 // User's email address
  name: string | null;           // User's display name (optional)
  avatar_url: string | null;     // URL to user's profile picture (optional)
  created_at: string;            // ISO 8601 timestamp of account creation
  updated_at: string;            // ISO 8601 timestamp of last profile update
}
```

**Usage**:
- Displayed in profile page
- Shown in app header
- Used for user identification in API calls

**Validation Rules**:
- `id`: Required, non-empty string
- `email`: Required, valid email format
- `name`: Optional, max 100 characters
- `avatar_url`: Optional, valid URL
- Timestamps: ISO 8601 format (e.g., "2026-02-06T10:30:00Z")

---

### Task

Represents a todo item belonging to a user.

```typescript
export interface Task {
  id: number;                    // Unique task identifier
  user_id: string;               // Owner's user ID (foreign key to User.id)
  title: string;                 // Task title (required)
  description: string | null;    // Task description (optional)
  completed: boolean;            // Completion status
  priority: 'low' | 'medium' | 'high' | null;  // Priority level (optional)
  due_date: string | null;       // ISO 8601 date string (optional)
  created_at: string;            // ISO 8601 timestamp of task creation
  updated_at: string;            // ISO 8601 timestamp of last update
}
```

**Usage**:
- Displayed in task list
- Edited in task form
- Filtered and sorted in dashboard

**Validation Rules**:
- `id`: Required, positive integer
- `user_id`: Required, matches authenticated user
- `title`: Required, 1-200 characters
- `description`: Optional, max 2000 characters
- `completed`: Required, boolean
- `priority`: Optional, one of: "low", "medium", "high"
- `due_date`: Optional, ISO 8601 date format
- Timestamps: ISO 8601 format

---

### Session

Represents the user's authentication session.

```typescript
export interface Session {
  token: string;                 // JWT token
  user: User;                    // User information
  expiresAt: string;             // ISO 8601 timestamp of token expiration
}
```

**Usage**:
- Managed by Better Auth
- Stored in httpOnly cookies
- Used for API authentication

**Validation Rules**:
- `token`: Required, valid JWT format
- `user`: Required, valid User object
- `expiresAt`: Required, ISO 8601 timestamp

---

## API Types

### API Response Wrapper

Generic wrapper for successful API responses.

```typescript
export interface ApiResponse<T> {
  data: T;                       // Response data (typed)
  message?: string;              // Optional success message
}
```

**Usage**:
- Wraps all successful API responses
- Provides consistent response structure
- Type parameter `T` specifies data type

**Example**:
```typescript
// Single task response
ApiResponse<Task>

// Task list response
ApiResponse<Task[]>

// User profile response
ApiResponse<User>
```

---

### API Error

Represents an error response from the API.

```typescript
export interface ApiError {
  detail: string;                // Human-readable error message
  code: string;                  // Machine-readable error code
  field?: string;                // Field name for validation errors (optional)
}
```

**Usage**:
- Thrown by API client on HTTP errors
- Displayed to users in error messages
- Used for field-specific validation errors

**Error Codes**:
- `UNAUTHORIZED`: Authentication required (401)
- `FORBIDDEN`: Access denied (403)
- `NOT_FOUND`: Resource not found (404)
- `VALIDATION_ERROR`: Invalid input (400)
- `INTERNAL_ERROR`: Server error (500)
- `TASK_NOT_FOUND`: Specific task not found
- `USER_NOT_FOUND`: Specific user not found

**Example**:
```typescript
{
  detail: "Task not found or you don't have permission to access it",
  code: "TASK_NOT_FOUND"
}

{
  detail: "Title must be at least 1 character",
  code: "VALIDATION_ERROR",
  field: "title"
}
```

---

## Form Data Types

### TaskCreateData

Data required to create a new task.

```typescript
export interface TaskCreateData {
  title: string;                 // Task title (required)
  description?: string;          // Task description (optional)
  priority?: 'low' | 'medium' | 'high';  // Priority level (optional)
  due_date?: string;             // ISO 8601 date string (optional)
}
```

**Usage**:
- Task creation form
- POST /api/v1/tasks request body

**Validation**:
- `title`: Required, 1-200 characters
- `description`: Optional, max 2000 characters
- `priority`: Optional, one of: "low", "medium", "high"
- `due_date`: Optional, ISO 8601 date format

---

### TaskUpdateData

Data for updating an existing task.

```typescript
export interface TaskUpdateData {
  title?: string;                // Updated title (optional)
  description?: string;          // Updated description (optional)
  completed?: boolean;           // Updated completion status (optional)
  priority?: 'low' | 'medium' | 'high' | null;  // Updated priority (optional)
  due_date?: string | null;      // Updated due date (optional)
}
```

**Usage**:
- Task edit form
- PUT /api/v1/tasks/{id} request body
- PATCH /api/v1/tasks/{id}/complete request body

**Validation**:
- All fields optional (partial update)
- Same validation rules as TaskCreateData when provided
- `null` values clear optional fields

---

### ProfileFormData

Data for updating user profile.

```typescript
export interface ProfileFormData {
  name: string;                  // Updated display name
  avatar?: File | null;          // New avatar image file (optional)
}
```

**Usage**:
- Profile edit form
- PUT /api/v1/users/me request body
- POST /api/v1/users/me/avatar request body (avatar only)

**Validation**:
- `name`: Required, 1-100 characters
- `avatar`: Optional, image file (JPEG, PNG, GIF), max 5MB

---

### SignUpFormData

Data for user registration.

```typescript
export interface SignUpFormData {
  email: string;                 // User's email address
  password: string;              // User's password
  name?: string;                 // User's display name (optional)
}
```

**Usage**:
- Sign up form
- POST /api/v1/auth/signup request body

**Validation**:
- `email`: Required, valid email format
- `password`: Required, min 8 characters
- `name`: Optional, max 100 characters

---

### SignInFormData

Data for user authentication.

```typescript
export interface SignInFormData {
  email: string;                 // User's email address
  password: string;              // User's password
}
```

**Usage**:
- Sign in form
- POST /api/v1/auth/signin request body

**Validation**:
- `email`: Required, valid email format
- `password`: Required

---

## UI State Types

### TaskFilter

Filter options for task list.

```typescript
export type TaskFilter = 'all' | 'active' | 'completed';
```

**Usage**:
- Task list filtering
- Local component state

**Values**:
- `all`: Show all tasks
- `active`: Show only incomplete tasks
- `completed`: Show only completed tasks

---

### TaskSort

Sort options for task list.

```typescript
export type TaskSort = 'created' | 'updated' | 'due_date' | 'priority';
```

**Usage**:
- Task list sorting
- Local component state

**Values**:
- `created`: Sort by creation date (newest first)
- `updated`: Sort by last update (newest first)
- `due_date`: Sort by due date (soonest first)
- `priority`: Sort by priority (high to low)

---

### LoadingState

Loading state for async operations.

```typescript
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';
```

**Usage**:
- Form submission states
- API call states
- Component loading indicators

**Values**:
- `idle`: No operation in progress
- `loading`: Operation in progress
- `success`: Operation completed successfully
- `error`: Operation failed

---

## Component Hierarchy

```text
App Layout (Root)
├── AuthProvider (Context)
│   └── Session state (user, isAuthenticated, isLoading)
│
├── Header (Navigation)
│   ├── Logo
│   ├── Navigation Links (Dashboard, Profile)
│   └── User Menu
│       ├── Avatar (User.avatar_url)
│       ├── Name (User.name)
│       └── Logout Button
│
├── Auth Pages (Public)
│   ├── SignIn Page
│   │   └── SignInForm
│   │       ├── State: SignInFormData
│   │       └── State: LoadingState
│   └── SignUp Page
│       └── SignUpForm
│           ├── State: SignUpFormData
│           └── State: LoadingState
│
├── Protected Layout (Auth Required)
│   ├── Dashboard Page
│   │   ├── State: Task[]
│   │   ├── State: TaskFilter
│   │   ├── State: TaskSort
│   │   ├── TaskFilters
│   │   └── TaskList
│   │       └── TaskCard (multiple)
│   │           └── Props: Task
│   │
│   ├── Task Detail/Edit Page
│   │   ├── State: Task
│   │   └── TaskForm
│   │       ├── Props: Task (for edit)
│   │       ├── State: TaskUpdateData
│   │       └── State: LoadingState
│   │
│   ├── New Task Page
│   │   └── TaskForm
│   │       ├── State: TaskCreateData
│   │       └── State: LoadingState
│   │
│   └── Profile Page
│       ├── State: User
│       ├── ProfileHeader
│       ├── ProfileAvatar
│       │   └── Props: User.avatar_url
│       └── ProfileForm
│           ├── State: ProfileFormData
│           └── State: LoadingState
│
└── UI Components (Reusable)
    ├── Button
    │   └── Props: variant, size, loading, disabled
    ├── Input
    │   └── Props: type, value, error, required
    ├── Card
    │   └── Props: children, className
    ├── Modal
    │   └── Props: isOpen, onClose, title, children
    └── LoadingSpinner
        └── Props: size, color
```

---

## Type Exports

All types should be exported from a central location for easy imports:

```typescript
// lib/types/index.ts
export type { User } from './user';
export type { Task, TaskCreateData, TaskUpdateData } from './task';
export type { Session } from './session';
export type { ApiResponse, ApiError } from './api';
export type {
  SignUpFormData,
  SignInFormData,
  ProfileFormData
} from './forms';
export type {
  TaskFilter,
  TaskSort,
  LoadingState
} from './ui';
```

**Usage**:
```typescript
import { Task, TaskCreateData, ApiError } from '@/lib/types';
```

---

## Validation Utilities

Helper functions for type validation:

```typescript
// lib/utils/validation.ts

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidTask(task: unknown): task is Task {
  return (
    typeof task === 'object' &&
    task !== null &&
    'id' in task &&
    'title' in task &&
    'completed' in task
  );
}

export function isValidUser(user: unknown): user is User {
  return (
    typeof user === 'object' &&
    user !== null &&
    'id' in task &&
    'email' in user
  );
}
```

---

## Summary

This data model provides:
- **Type Safety**: All data structures are strongly typed
- **Consistency**: Uniform naming and structure conventions
- **Validation**: Clear validation rules for each field
- **Documentation**: Comprehensive descriptions and usage examples
- **Maintainability**: Centralized type definitions

**Next Steps**: Use these types throughout the application to ensure type safety and consistency.
