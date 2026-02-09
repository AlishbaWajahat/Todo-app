"""
Agent Chat Endpoint

This module provides the FastAPI endpoint for the stateless task agent.
Users can send natural language messages to manage their tasks.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from agent.agent import process_request, AgentRequest, AgentResponse


router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    """Request schema for agent chat endpoint."""
    user_id: str = Field(..., min_length=1, description="Pre-authenticated user identifier")
    message: str = Field(..., min_length=1, max_length=1000, description="Natural language message")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "user_id": "user-123",
                    "message": "Create a task to buy groceries"
                },
                {
                    "user_id": "user-123",
                    "message": "Show me my tasks"
                }
            ]
        }


class ChatResponse(BaseModel):
    """Response schema for agent chat endpoint."""
    response: str = Field(..., description="Natural language response from agent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context for debugging")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "response": "Task created: Buy groceries",
                    "metadata": {
                        "intent": "CREATE",
                        "tool_called": "add_task",
                        "confidence": 0.95,
                        "execution_time_ms": 312
                    }
                }
            ]
        }


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to task agent",
    description="""
    Process natural language message and invoke appropriate MCP task tool.

    The agent is stateless - each request is independent. It can:
    - Create tasks: "Create a task to buy milk"
    - List tasks: "Show me my tasks"
    - Complete tasks: "Mark 'Buy milk' as done"
    - Update tasks: "Change 'Buy milk' to 'Buy organic milk'"
    - Delete tasks: "Delete task 5"

    The agent returns natural language responses with optional metadata for debugging.
    """
)
async def chat_with_agent(request: ChatRequest) -> ChatResponse:
    """
    Process a natural language task management request.

    Args:
        request: ChatRequest with user_id and message

    Returns:
        ChatResponse with natural language response and metadata

    Raises:
        HTTPException: 400 if validation fails, 500 if internal error occurs

    Examples:
        Request: {"user_id": "user-123", "message": "Create a task to buy milk"}
        Response: {"response": "Task created: Buy milk", "metadata": {...}}
    """
    try:
        # Validate user_id
        if not request.user_id or len(request.user_id.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID is required and cannot be empty"
            )

        # Validate message
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        if len(request.message) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message must be under 1000 characters"
            )

        # Process request through agent
        agent_response = await process_request(request.user_id, request.message)

        # Return response
        return ChatResponse(
            response=agent_response.response,
            metadata=agent_response.metadata
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error and return generic error message
        # In production, use proper logging
        print(f"Error in chat_with_agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred. Please try again."
        )
