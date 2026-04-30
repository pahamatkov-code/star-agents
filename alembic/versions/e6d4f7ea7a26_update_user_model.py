"""Update User model

Revision ID: e6d4f7ea7a26
Revises: d501a4158a70
Create Date: 2026-04-21 12:03:41.470319
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6d4f7ea7a26'
down_revision: Union[str, Sequence[str], None] = 'd501a4158a70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite does NOT support ALTER COLUMN, so we only add the new column.
    op.add_column(
        'users',
        sa.Column('balance', sa.Integer(), nullable=False, server_default='0')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'balance')
