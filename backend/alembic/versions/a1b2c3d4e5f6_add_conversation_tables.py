"""add conversation tables

Revision ID: a1b2c3d4e5f6
Revises: 4517dcc2e52b
Create Date: 2026-02-09 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '4517dcc2e52b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create conversation tables."""

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)
    op.create_index('idx_conversations_user_updated', 'conversations', ['user_id', 'updated_at'], unique=False)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('USER', 'ASSISTANT', 'SYSTEM', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('conversation_id', 'sequence_number', name='unique_conversation_sequence'),
        sa.CheckConstraint('sequence_number >= 0', name='check_sequence_positive'),
        sa.CheckConstraint('tokens_used IS NULL OR tokens_used >= 0', name='check_tokens_positive')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)
    op.create_index('idx_messages_conversation_sequence', 'messages', ['conversation_id', 'sequence_number'], unique=False)

    # Create tool_calls table
    op.create_table(
        'tool_calls',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('message_id', sa.BigInteger(), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('tool_input', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('tool_output', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'SUCCESS', 'ERROR', name='toolcallstatus'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('execution_time_ms IS NULL OR execution_time_ms >= 0', name='check_execution_time_positive'),
        sa.CheckConstraint('completed_at IS NULL OR completed_at >= created_at', name='check_completion_time')
    )
    op.create_index(op.f('ix_tool_calls_message_id'), 'tool_calls', ['message_id'], unique=False)
    op.create_index(op.f('ix_tool_calls_tool_name'), 'tool_calls', ['tool_name'], unique=False)


def downgrade() -> None:
    """Downgrade schema - drop conversation tables."""

    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_index(op.f('ix_tool_calls_tool_name'), table_name='tool_calls')
    op.drop_index(op.f('ix_tool_calls_message_id'), table_name='tool_calls')
    op.drop_table('tool_calls')

    op.drop_index('idx_messages_conversation_sequence', table_name='messages')
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')

    op.drop_index('idx_conversations_user_updated', table_name='conversations')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_table('conversations')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS toolcallstatus')
    op.execute('DROP TYPE IF EXISTS messagerole')
