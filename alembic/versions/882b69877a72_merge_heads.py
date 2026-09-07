"""merge heads

Revision ID: 882b69877a72
Revises: 20260819_init_models, 865bbd35d456
Create Date: 2026-08-19 15:30:47.827687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '882b69877a72'
down_revision: Union[str, Sequence[str], None] = ('20260819_init_models', '865bbd35d456')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
