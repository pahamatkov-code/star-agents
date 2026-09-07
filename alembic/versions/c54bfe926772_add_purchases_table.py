from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c54bfe926772'
down_revision: str = '2572_cleanup_chat_messages'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'purchases',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
        sa.Column('agent_id', sa.Integer, sa.ForeignKey('agents.id', ondelete="CASCADE"), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column('status', sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()'))
    )

    # Індекси для швидкого пошуку
    op.create_index("ix_purchases_user_id", "purchases", ["user_id"], unique=False)
    op.create_index("ix_purchases_agent_id", "purchases", ["agent_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_purchases_user_id", table_name="purchases")
    op.drop_index("ix_purchases_agent_id", table_name="purchases")
    op.drop_table('purchases')
