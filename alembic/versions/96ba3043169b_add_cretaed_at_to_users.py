"""add created_at to users

Revision ID: 96ba3043169b
Revises: 809908ef6972
Create Date: 2025-09-20 15:48:01.967458
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96ba3043169b'
down_revision: Union[str, Sequence[str], None] = '809908ef6972'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'created_at')