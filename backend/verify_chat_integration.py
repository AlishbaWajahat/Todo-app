"""
Verify Chat Integration - Database Check

This script verifies that conversations, messages, and tool calls
are being saved correctly to the database.
"""
from core.database import get_session
from sqlalchemy import text
from models import Conversation, Message, ToolCall
from sqlmodel import select

def verify_chat_integration():
    """Verify chat data is being saved to database."""
    session = next(get_session())

    try:
        print("\n" + "="*60)
        print("CHAT INTEGRATION DATABASE VERIFICATION")
        print("="*60)

        # Check conversations
        conversations = session.exec(select(Conversation)).all()
        print(f"\n[INFO] Total Conversations: {len(conversations)}")

        if conversations:
            print("\n[SUCCESS] Conversations found:")
            for conv in conversations[-5:]:  # Show last 5
                print(f"  - ID: {conv.id}")
                print(f"    User ID: {conv.user_id}")
                print(f"    Title: {conv.title}")
                print(f"    Created: {conv.created_at}")
                print(f"    Updated: {conv.updated_at}")
                print()
        else:
            print("[WARNING] No conversations found. Please test the chat UI first.")
            return

        # Check messages
        messages = session.exec(select(Message)).all()
        print(f"[INFO] Total Messages: {len(messages)}")

        if messages:
            print("\n[SUCCESS] Recent messages:")
            for msg in messages[-10:]:  # Show last 10
                print(f"  - ID: {msg.id} | Seq: {msg.sequence_number}")
                print(f"    Conversation: {msg.conversation_id}")
                print(f"    Role: {msg.role.value}")
                print(f"    Content: {msg.content[:80]}{'...' if len(msg.content) > 80 else ''}")
                print(f"    Created: {msg.created_at}")
                if msg.model:
                    print(f"    Model: {msg.model}")
                if msg.tokens_used:
                    print(f"    Tokens: {msg.tokens_used}")
                print()

        # Check tool calls
        tool_calls = session.exec(select(ToolCall)).all()
        print(f"[INFO] Total Tool Calls: {len(tool_calls)}")

        if tool_calls:
            print("\n[SUCCESS] Recent tool calls:")
            for tc in tool_calls[-5:]:  # Show last 5
                print(f"  - ID: {tc.id}")
                print(f"    Message ID: {tc.message_id}")
                print(f"    Tool: {tc.tool_name}")
                print(f"    Status: {tc.status.value}")
                print(f"    Input: {tc.tool_input}")
                if tc.tool_output:
                    print(f"    Output: {tc.tool_output}")
                if tc.execution_time_ms:
                    print(f"    Execution Time: {tc.execution_time_ms}ms")
                print()
        else:
            print("[INFO] No tool calls found yet (normal if only greeting messages sent).")

        # Verify data integrity
        print("\n" + "="*60)
        print("DATA INTEGRITY CHECKS")
        print("="*60)

        # Check for orphaned messages
        orphaned_messages = session.exec(
            text("""
                SELECT COUNT(*)
                FROM messages m
                LEFT JOIN conversations c ON m.conversation_id = c.id
                WHERE c.id IS NULL
            """)
        ).first()

        if orphaned_messages and orphaned_messages[0] > 0:
            print(f"[ERROR] Found {orphaned_messages[0]} orphaned messages!")
        else:
            print("[SUCCESS] No orphaned messages found.")

        # Check for orphaned tool calls
        orphaned_tools = session.exec(
            text("""
                SELECT COUNT(*)
                FROM tool_calls tc
                LEFT JOIN messages m ON tc.message_id = m.id
                WHERE m.id IS NULL
            """)
        ).first()

        if orphaned_tools and orphaned_tools[0] > 0:
            print(f"[ERROR] Found {orphaned_tools[0]} orphaned tool calls!")
        else:
            print("[SUCCESS] No orphaned tool calls found.")

        # Check sequence numbers are correct
        for conv in conversations:
            messages_in_conv = session.exec(
                select(Message)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.sequence_number)
            ).all()

            expected_seq = 0
            for msg in messages_in_conv:
                if msg.sequence_number != expected_seq:
                    print(f"[ERROR] Sequence number mismatch in conversation {conv.id}")
                    print(f"  Expected: {expected_seq}, Got: {msg.sequence_number}")
                    break
                expected_seq += 1
            else:
                if messages_in_conv:
                    print(f"[SUCCESS] Sequence numbers correct for conversation {conv.id}")

        print("\n" + "="*60)
        print("VERIFICATION COMPLETE")
        print("="*60 + "\n")

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    verify_chat_integration()
