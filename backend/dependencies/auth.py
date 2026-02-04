"""
Authentication Dependencies.

Provides reusable dependencies for accessing authenticated user information
in route handlers.

Usage:
    @app.get("/tasks")
    def get_tasks(current_user: User = Depends(get_current_user)):
        # current_user is guaranteed to exist and be valid
        user_id = current_user.id
        ...
"""
from fastapi import Request, HTTPException, Depends
from models.user import User


def get_current_user(request: Request) -> User:
    """
    FastAPI dependency to retrieve authenticated user from request state.

    This dependency extracts the User object that was stored by the
    authentication middleware in request.state.user after JWT validation
    and user provisioning.

    Returns:
        User: SQLModel User object with attributes:
            - id (str): User ID from JWT "sub" claim (primary key)
            - email (str): User email address
            - name (str | None): User display name (optional)
            - avatar_url (str | None): User profile picture URL (optional)
            - created_at (datetime): When user record was created
            - updated_at (datetime): When user record was last updated

    Raises:
        HTTPException: 401 if user not found in request.state
            (indicates middleware didn't run or authentication failed)

    Usage:
        @app.get("/tasks")
        def get_tasks(current_user: User = Depends(get_current_user)):
            user_id = current_user.id
            # Query tasks for this user
            ...

    Security Notes:
    - This dependency should be used on all protected routes
    - User identity is guaranteed to be valid (middleware validated JWT)
    - User object is type-safe (SQLModel with proper type hints)
    - If this raises 401, it indicates a configuration error
      (middleware not registered or route bypassed middleware)
    """
    if not hasattr(request.state, "user"):
        # User not found in request state
        # This should never happen if middleware is properly configured
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return request.state.user
