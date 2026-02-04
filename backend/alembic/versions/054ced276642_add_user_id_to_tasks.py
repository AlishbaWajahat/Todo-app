"""add_user_id_to_tasks

Revision ID: 054ced276642
Revises: 53eb16208b05
Create Date: 2026-02-05 02:17:23.068953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '054ced276642'
down_revision: Union[str, Sequence[str], None] = '53eb16208b05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Update tasks table to support multi-user functionality.

    Changes:
    - Change user_id from INTEGER to VARCHAR (to match users.id type)
    - Add foreign key constraint to users.id with ON DELETE CASCADE
    - Create index on user_id for fast user-scoped queries
    - Create composite index on (id, user_id) for single-task lookups with user validation
    - Add priority and due_date columns
    - Update description max length to 2000
    """
    # Step 1: Rename the table to preserve data
    op.rename_table('task', 'task_old')

    # Step 2: Create new tasks table with correct schema
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Step 3: Add foreign key constraint with CASCADE delete
    op.create_foreign_key(
        'fk_tasks_user_id',
        'tasks',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Step 4: Create index on user_id for fast user-scoped queries
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])

    # Step 5: Create composite index on (id, user_id) for single-task lookups
    op.create_index('idx_tasks_id_user_id', 'tasks', ['id', 'user_id'])

    # Step 6: Drop old table (data migration not needed for fresh MVP)
    op.drop_table('task_old')


def downgrade() -> None:
    """
    Revert tasks table to original schema.

    Removes multi-user support and reverts to INTEGER user_id.
    """
    # Step 1: Drop indexes
    op.drop_index('idx_tasks_id_user_id', table_name='tasks')
    op.drop_index('idx_tasks_user_id', table_name='tasks')

    # Step 2: Drop foreign key constraint
    op.drop_constraint('fk_tasks_user_id', 'tasks', type_='foreignkey')

    # Step 3: Rename current table
    op.rename_table('tasks', 'tasks_old')

    # Step 4: Recreate original task table with INTEGER user_id
    op.create_table(
        'task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Step 5: Drop new table
    op.drop_table('tasks_old')
