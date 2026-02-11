"""
ChatKit Adapter Endpoint

Uses the openai-chatkit Python Server SDK to handle the ChatKit protocol.
The SDK manages all SSE event formatting, request routing (threads.list,
threads.create, etc.), and response serialization.

This implementation persists all conversations and messages to the database.
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, Response
from datetime import datetime
from uuid import uuid4, UUID
from collections.abc import AsyncIterator
from sqlmodel import Session, select
from typing import Optional

from chatkit.server import ChatKitServer, StreamingResult, NonStreamingResult
from chatkit.store import Store, NotFoundError
from chatkit.types import (
    ThreadMetadata,
    ThreadStreamEvent,
    ThreadItemDoneEvent,
    AssistantMessageItem,
    AssistantMessageContent,
    UserMessageItem,
    Page,
)

from dependencies.auth import get_current_user
from models import User, Conversation, Message, MessageRole, ToolCall, ToolCallStatus
from core.database import get_session
from agent.agent import process_request

router = APIRouter(prefix="/chatkit", tags=["chatkit"])


def generate_conversation_title(first_message: str) -> str:
    """
    Generate a meaningful title for a conversation based on the first user message.

    Extracts key topics and actions to create a concise, descriptive title.
    Falls back to "New conversation" if message is too short or generic.
    """
    message = first_message.strip()

    # Handle greetings and very short messages
    if len(message) < 10 or message.lower() in ["hi", "hello", "hey", "yo", "sup"]:
        return "New conversation"

    # Extract task-related keywords for better titles
    message_lower = message.lower()

    # Check for specific task operations
    if "add" in message_lower or "create" in message_lower:
        if "task" in message_lower:
            # Extract task title if possible
            for word in message.split():
                if len(word) > 4 and word.lower() not in ["task", "create", "please", "could", "would"]:
                    return f"Add task: {word.capitalize()}..."
            return "Add new task"
    elif "complete" in message_lower or "finish" in message_lower or "done" in message_lower:
        return "Complete tasks"
    elif "update" in message_lower or "edit" in message_lower or "change" in message_lower:
        return "Update tasks"
    elif "delete" in message_lower or "remove" in message_lower:
        return "Delete tasks"
    elif "list" in message_lower or "show" in message_lower or "see" in message_lower:
        return "View tasks"

    # For casual conversation, use first few words
    words = message.split()[:5]
    title = " ".join(words)

    # Truncate to 50 chars max
    if len(title) > 50:
        title = title[:47] + "..."

    return title.capitalize() if title else "New conversation"


# ---------------------------------------------------------------------------
# Database-backed store for ChatKit SDK
# ---------------------------------------------------------------------------
class DatabaseStore(Store[dict]):
    """Database-backed store for ChatKit SDK.

    Persists threads (conversations) and items (messages) to PostgreSQL.
    Context must include: user_id (str) and session (Session).
    """

    def generate_thread_id(self, context: dict) -> str:
        """Generate new conversation UUID."""
        return str(uuid4())

    def generate_item_id(self, item_type, thread, context: dict) -> str:
        """Generate new message ID (will be replaced by DB auto-increment)."""
        return str(uuid4())

    async def load_threads(self, limit, after, order, context: dict) -> Page:
        """Load user's conversations from database."""
        session: Session = context["session"]
        user_id: str = context["user_id"]

        # Query conversations for this user
        query = select(Conversation).where(Conversation.user_id == user_id)

        # Apply ordering
        if order == "desc":
            query = query.order_by(Conversation.updated_at.desc())
        else:
            query = query.order_by(Conversation.updated_at.asc())

        conversations = session.exec(query.limit(limit)).all()

        # Convert to ThreadMetadata
        threads = [
            ThreadMetadata(
                id=str(conv.id),
                created_at=conv.created_at,
                metadata={"title": conv.title or "New conversation"}
            )
            for conv in conversations
        ]

        return Page(data=threads, has_more=False, after=None)

    async def load_thread(self, thread_id, context: dict) -> ThreadMetadata:
        """Load specific conversation from database."""
        session: Session = context["session"]
        user_id: str = context["user_id"]

        # Parse UUID
        try:
            conv_uuid = UUID(thread_id)
        except ValueError:
            raise NotFoundError(f"Invalid thread ID: {thread_id}")

        # Query conversation
        conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == conv_uuid)
            .where(Conversation.user_id == user_id)
        ).first()

        if not conversation:
            raise NotFoundError(f"Thread {thread_id} not found")

        return ThreadMetadata(
            id=str(conversation.id),
            created_at=conversation.created_at,
            metadata={"title": conversation.title or "New conversation"}
        )

    async def save_thread(self, thread, context: dict) -> None:
        """Save conversation to database."""
        session: Session = context["session"]
        user_id: str = context["user_id"]

        # Parse UUID
        conv_uuid = UUID(thread.id)

        # Check if exists
        existing = session.exec(
            select(Conversation)
            .where(Conversation.id == conv_uuid)
            .where(Conversation.user_id == user_id)
        ).first()

        if existing:
            # Update timestamp
            existing.updated_at = datetime.utcnow()
            session.add(existing)
        else:
            # Create new conversation
            conversation = Conversation(
                id=conv_uuid,
                user_id=user_id,
                title=thread.metadata.get("title") if thread.metadata else None,
                created_at=thread.created_at,
                updated_at=datetime.utcnow()
            )
            session.add(conversation)

        session.commit()

    async def delete_thread(self, thread_id, context: dict) -> None:
        """Delete conversation from database."""
        session: Session = context["session"]
        user_id: str = context["user_id"]

        conv_uuid = UUID(thread_id)
        conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == conv_uuid)
            .where(Conversation.user_id == user_id)
        ).first()

        if conversation:
            session.delete(conversation)
            session.commit()

    async def load_thread_items(self, thread_id, after, limit, order, context: dict) -> Page:
        """Load messages from database."""
        session: Session = context["session"]
        user_id: str = context["user_id"]

        conv_uuid = UUID(thread_id)

        # Verify conversation belongs to user
        conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == conv_uuid)
            .where(Conversation.user_id == user_id)
        ).first()

        if not conversation:
            raise NotFoundError(f"Thread {thread_id} not found")

        # Query messages
        query = select(Message).where(Message.conversation_id == conv_uuid)

        if order == "desc":
            query = query.order_by(Message.sequence_number.desc())
        else:
            query = query.order_by(Message.sequence_number.asc())

        messages = session.exec(query.limit(limit)).all()

        # Convert to ChatKit items
        items = []
        for msg in messages:
            if msg.role == MessageRole.USER:
                items.append(UserMessageItem(
                    id=str(msg.id),
                    thread_id=thread_id,
                    created_at=msg.created_at,
                    content=[{"type": "text", "text": msg.content}]
                ))
            elif msg.role == MessageRole.ASSISTANT:
                items.append(AssistantMessageItem(
                    id=str(msg.id),
                    thread_id=thread_id,
                    created_at=msg.created_at,
                    content=[AssistantMessageContent(text=msg.content, annotations=[])]
                ))

        return Page(data=items, has_more=False, after=None)

    async def load_item(self, thread_id, item_id, context: dict):
        """Load specific message from database."""
        session: Session = context["session"]
        user_id: str = context["user_id"]

        conv_uuid = UUID(thread_id)
        msg_id = int(item_id)

        # Verify conversation belongs to user
        conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == conv_uuid)
            .where(Conversation.user_id == user_id)
        ).first()

        if not conversation:
            raise NotFoundError(f"Thread {thread_id} not found")

        # Load message
        message = session.exec(
            select(Message)
            .where(Message.id == msg_id)
            .where(Message.conversation_id == conv_uuid)
        ).first()

        if not message:
            raise NotFoundError(f"Item {item_id} not found")

        # Convert to ChatKit item
        if message.role == MessageRole.USER:
            return UserMessageItem(
                id=str(message.id),
                thread_id=thread_id,
                created_at=message.created_at,
                content=[{"type": "text", "text": message.content}]
            )
        else:
            return AssistantMessageItem(
                id=str(message.id),
                thread_id=thread_id,
                created_at=message.created_at,
                content=[AssistantMessageContent(text=message.content, annotations=[])]
            )

    async def save_item(self, thread_id, item, context: dict) -> None:
        """Save message to database."""
        await self.add_thread_item(thread_id, item, context)

    async def add_thread_item(self, thread_id, item, context: dict) -> None:
        """Add message to conversation in database."""
        session: Session = context["session"]
        user_id: str = context["user_id"]

        conv_uuid = UUID(thread_id)

        # Verify conversation belongs to user
        conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == conv_uuid)
            .where(Conversation.user_id == user_id)
        ).first()

        if not conversation:
            raise NotFoundError(f"Thread {thread_id} not found")

        # Get next sequence number
        last_message = session.exec(
            select(Message)
            .where(Message.conversation_id == conv_uuid)
            .order_by(Message.sequence_number.desc())
        ).first()

        next_sequence = 0 if last_message is None else last_message.sequence_number + 1

        # Extract content
        content_text = ""
        if hasattr(item, 'content') and item.content:
            for part in item.content:
                if hasattr(part, 'text'):
                    content_text = part.text
                    break
                elif isinstance(part, dict) and 'text' in part:
                    content_text = part['text']
                    break

        # Determine role
        role = MessageRole.ASSISTANT if isinstance(item, AssistantMessageItem) else MessageRole.USER

        # Create message
        message = Message(
            conversation_id=conv_uuid,
            role=role,
            content=content_text,
            sequence_number=next_sequence,
            created_at=item.created_at if hasattr(item, 'created_at') else datetime.utcnow(),
            model="gemini-2.5-flash" if role == MessageRole.ASSISTANT else None
        )

        session.add(message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

        session.commit()

    async def delete_thread_item(self, thread_id, item_id, context: dict) -> None:
        """Delete message from database."""
        session: Session = context["session"]
        user_id: str = context["user_id"]

        conv_uuid = UUID(thread_id)
        msg_id = int(item_id)

        # Verify conversation belongs to user
        conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == conv_uuid)
            .where(Conversation.user_id == user_id)
        ).first()

        if not conversation:
            raise NotFoundError(f"Thread {thread_id} not found")

        # Delete message
        message = session.exec(
            select(Message)
            .where(Message.id == msg_id)
            .where(Message.conversation_id == conv_uuid)
        ).first()

        if message:
            session.delete(message)
            session.commit()

    async def save_attachment(self, attachment, context: dict) -> None:
        """Attachments not supported."""
        pass

    async def load_attachment(self, attachment_id, context: dict):
        """Attachments not supported."""
        raise NotFoundError(f"Attachment {attachment_id} not found")

    async def delete_attachment(self, attachment_id, context: dict) -> None:
        """Attachments not supported."""
        pass


# ---------------------------------------------------------------------------
# ChatKit Server (handles protocol + delegates to agent)
# ---------------------------------------------------------------------------
class TaskAssistantServer(ChatKitServer[dict]):
    """ChatKit server that delegates message processing to the task agent."""

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        session: Session = context.get("session")
        user_id = context.get("user_id", "")

        # Extract user text from the message
        user_text = ""
        if input_user_message and input_user_message.content:
            for part in input_user_message.content:
                if hasattr(part, "text"):
                    user_text = part.text
                    break

        if not user_text:
            user_text = "hello"

        print(f"ChatKit processing message for user {user_id}: {user_text}")

        # Check if this is the first message in the conversation
        conv_uuid = UUID(thread.id)
        conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == conv_uuid)
            .where(Conversation.user_id == user_id)
        ).first()

        # Generate title if this is a new conversation (no messages yet or no title)
        if conversation:
            # Count messages in this conversation
            from sqlalchemy import func
            message_count = session.exec(
                select(func.count(Message.id))
                .where(Message.conversation_id == conv_uuid)
            ).one()

            # Generate title only for first user message if no title exists
            if message_count == 0 and not conversation.title:
                title = generate_conversation_title(user_text)
                conversation.title = title
                session.add(conversation)
                session.commit()
                print(f"Generated conversation title: {title}")

        # Fetch recent conversation history for context (last 10 messages)
        conversation_history = []
        if conversation:
            recent_messages = session.exec(
                select(Message)
                .where(Message.conversation_id == conv_uuid)
                .order_by(Message.sequence_number.desc())
                .limit(10)
            ).all()

            # Reverse to get chronological order and format for agent
            for msg in reversed(recent_messages):
                conversation_history.append({
                    "role": msg.role.value,
                    "content": msg.content
                })

        # Process through the existing agent (pass conversation_id and history for context)
        agent_response = await process_request(
            str(user_id),
            user_text,
            str(thread.id),
            conversation_history
        )

        # Create assistant message
        assistant_item = AssistantMessageItem(
            id=self.store.generate_item_id("message", thread, context),
            thread_id=thread.id,
            created_at=datetime.utcnow(),
            content=[AssistantMessageContent(
                text=agent_response.response,
                annotations=[],
            )],
        )

        # Yield the completed assistant message
        # Note: ChatKit SDK will automatically save this via store.add_thread_item()
        yield ThreadItemDoneEvent(item=assistant_item)

        # After message is saved, record tool call if one was made
        if agent_response.metadata and agent_response.metadata.get("tool_called"):
            # Get the assistant message that was just saved
            assistant_message = session.exec(
                select(Message)
                .where(Message.conversation_id == conv_uuid)
                .where(Message.role == MessageRole.ASSISTANT)
                .order_by(Message.sequence_number.desc())
            ).first()

            if assistant_message:
                # Create tool call record
                tool_call = ToolCall(
                    message_id=assistant_message.id,
                    tool_name=agent_response.metadata["tool_called"],
                    tool_input={"intent": agent_response.metadata.get("intent", "")},
                    tool_output={"response": agent_response.response},
                    status=ToolCallStatus.SUCCESS,
                    execution_time_ms=agent_response.metadata.get("execution_time_ms", 0),
                    created_at=assistant_message.created_at,
                    completed_at=datetime.utcnow()
                )
                session.add(tool_call)
                session.commit()
                print(f"Saved tool call: {tool_call.tool_name} for message {assistant_message.id}")


# Singleton instances
_store = DatabaseStore()
_server = TaskAssistantServer(store=_store)


# ---------------------------------------------------------------------------
# CORS pre-flight (no auth)
# ---------------------------------------------------------------------------
@router.options("")
async def chatkit_options():
    return JSONResponse(content={}, status_code=200)


# ---------------------------------------------------------------------------
# Chat History Management Endpoints
# ---------------------------------------------------------------------------
@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get all chat conversations for the current user.

    Returns list of conversations ordered by most recent first.
    """
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    print(f"Found {len(conversations)} conversations for user {current_user.id}")
    for conv in conversations:
        print(f"  - {conv.id}: {conv.title} (updated: {conv.updated_at})")

    return {
        "conversations": [
            {
                "id": str(conv.id),
                "title": conv.title or "New conversation",
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            }
            for conv in conversations
        ]
    }


@router.delete("/history/{conversation_id}")
async def delete_chat_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete a specific chat conversation and all its messages.

    Only the owner can delete their conversations.
    """
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID format"
        )

    # Find conversation
    conversation = session.exec(
        select(Conversation)
        .where(Conversation.id == conv_uuid)
        .where(Conversation.user_id == current_user.id)
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Delete conversation (messages will be cascade deleted)
    session.delete(conversation)
    session.commit()

    return {"message": "Conversation deleted successfully"}


# ---------------------------------------------------------------------------
# Main ChatKit endpoint (authenticated)
# ---------------------------------------------------------------------------
@router.post("")
async def chatkit_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Single ChatKit protocol endpoint.

    The SDK's process() method handles all request types:
    threads.list, threads.create, threads.retrieve, etc.

    All conversations and messages are persisted to the database.
    """
    print(f"ChatKit endpoint received request for user ID: {current_user.id}")
    body = await request.body()

    # Pass user context and database session so the store can persist data
    context = {
        "user_id": current_user.id,
        "session": session
    }

    result = await _server.process(body, context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(
            result,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    else:
        return Response(
            content=result.json,
            media_type="application/json",
        )
