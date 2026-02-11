"""
Task CRUD endpoints with strict user isolation.

All endpoints enforce user-scoped queries to prevent cross-user data access.
Users can only access, modify, or delete their own tasks.

Security Model:
- All endpoints require JWT authentication (enforced by middleware)
- user_id is extracted from authenticated user (not from request body)
- All queries filter by current_user.id
- Returns 404 (not 403) for unauthorized access to prevent information leakage
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import logging

from core.database import get_session
from models.task import Task
from models.user import User
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from dependencies.auth import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high)"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for authenticated user.

    Returns a list of all tasks belonging to the authenticated user.
    Supports optional filtering by completion status and priority.

    Security:
    - Only returns tasks where user_id = current_user.id
    - User cannot access other users' tasks

    Args:
        completed: Optional filter by completion status (true/false)
        priority: Optional filter by priority level (low, medium, high)
        current_user: Authenticated user (injected by dependency)
        session: Database session (injected)

    Returns:
        List[TaskResponse]: List of user's tasks (empty list if none)

    Raises:
        HTTPException 401: Authentication required (handled by middleware)
    """
    try:
        # Build query with user isolation
        statement = select(Task).where(Task.user_id == current_user.id)

        # Apply optional filters
        if completed is not None:
            statement = statement.where(Task.completed == completed)
        if priority is not None:
            statement = statement.where(Task.priority == priority)

        # Execute query
        tasks = session.exec(statement).all()

        logger.info(f"User {current_user.id} retrieved {len(tasks)} tasks")
        return tasks

    except Exception as e:
        logger.error(f"Failed to retrieve tasks for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tasks"
        )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    response: Response,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for authenticated user.

    Creates a task with user_id set to the authenticated user's ID.
    Client cannot specify user_id (prevents privilege escalation).

    Security:
    - user_id is set from current_user.id (not from request body)
    - User can only create tasks for themselves

    Args:
        task_data: Task creation data (title, description, priority, due_date)
        response: Response object for setting Location header
        current_user: Authenticated user (injected by dependency)
        session: Database session (injected)

    Returns:
        TaskResponse: Created task with id and timestamps

    Raises:
        HTTPException 400: Invalid input data (Pydantic validation)
        HTTPException 401: Authentication required (handled by middleware)
    """
    try:
        # Create Task model with user_id from authenticated user
        task = Task(
            user_id=current_user.id,
            **task_data.model_dump()
        )

        # Save to database
        session.add(task)
        session.commit()
        session.refresh(task)

        # Set Location header per REST best practices
        response.headers["Location"] = f"/tasks/{task.id}"

        logger.info(f"Task created: id={task.id}, user_id={current_user.id}")
        return task

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create task for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID.

    Returns task only if it belongs to the authenticated user.
    Returns 404 if task doesn't exist OR belongs to another user
    (prevents information leakage about other users' tasks).

    Security:
    - Query filters by both task_id AND user_id
    - Returns 404 (not 403) to prevent information leakage
    - User cannot determine if task exists for another user

    Args:
        task_id: Task identifier
        current_user: Authenticated user (injected by dependency)
        session: Database session (injected)

    Returns:
        TaskResponse: Task details

    Raises:
        HTTPException 404: Task not found or user doesn't have permission
        HTTPException 401: Authentication required (handled by middleware)
    """
    try:
        # Query with user isolation (composite index on id, user_id)
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
        task = session.exec(statement).first()

        if not task:
            # Return 404 (not 403) to prevent information leakage
            # User cannot determine if task exists for another user
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or you don't have permission to access it"
            )

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve task {task_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task"
        )


@router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a task (partial update - only provided fields are updated).

    Updates task only if it belongs to the authenticated user.
    Returns 404 if task doesn't exist OR belongs to another user.

    Security:
    - Query filters by both task_id AND user_id
    - user_id cannot be changed (not accepted in request body)
    - Returns 404 (not 403) to prevent information leakage

    Args:
        task_id: Task identifier
        task_data: Updated task data (only provided fields)
        current_user: Authenticated user (injected by dependency)
        session: Database session (injected)

    Returns:
        TaskResponse: Updated task

    Raises:
        HTTPException 404: Task not found or user doesn't have permission
        HTTPException 400: Invalid input data (Pydantic validation)
        HTTPException 401: Authentication required (handled by middleware)
    """
    try:
        # Query with user isolation
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
        task = session.exec(statement).first()

        if not task:
            # Return 404 (not 403) to prevent information leakage
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or you don't have permission to access it"
            )

        # Update only provided fields (partial update)
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        # Always update the updated_at timestamp
        task.updated_at = datetime.utcnow()

        # Save changes
        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Task updated: id={task_id}, user_id={current_user.id}")
        return task

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update task {task_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.patch("/{task_id}/complete", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def toggle_task_complete(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle task completion status.

    Toggles the completed field between true and false.
    Updates task only if it belongs to the authenticated user.
    Returns 404 if task doesn't exist OR belongs to another user.

    Security:
    - Query filters by both task_id AND user_id
    - Returns 404 (not 403) to prevent information leakage

    Args:
        task_id: Task identifier
        current_user: Authenticated user (injected by dependency)
        session: Database session (injected)

    Returns:
        TaskResponse: Updated task with toggled completion status

    Raises:
        HTTPException 404: Task not found or user doesn't have permission
        HTTPException 401: Authentication required (handled by middleware)
    """
    try:
        # Query with user isolation
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
        task = session.exec(statement).first()

        if not task:
            # Return 404 (not 403) to prevent information leakage
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or you don't have permission to access it"
            )

        # Toggle completion status
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        # Save changes
        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Task completion toggled: id={task_id}, completed={task.completed}, user_id={current_user.id}")
        return task

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to toggle task completion {task_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle task completion"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a task.

    Deletes task only if it belongs to the authenticated user.
    Returns 404 if task doesn't exist OR belongs to another user.

    Security:
    - Query filters by both task_id AND user_id
    - Returns 404 (not 403) to prevent information leakage
    - User cannot determine if task exists for another user

    Args:
        task_id: Task identifier
        current_user: Authenticated user (injected by dependency)
        session: Database session (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: Task not found or user doesn't have permission
        HTTPException 401: Authentication required (handled by middleware)
    """
    try:
        # Query with user isolation
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
        task = session.exec(statement).first()

        if not task:
            # Return 404 (not 403) to prevent information leakage
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or you don't have permission to access it"
            )

        # Delete task
        session.delete(task)
        session.commit()

        logger.info(f"Task deleted: id={task_id}, user_id={current_user.id}")
        return None

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete task {task_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )
