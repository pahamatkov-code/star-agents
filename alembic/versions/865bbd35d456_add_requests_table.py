from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '865bbd35d456'        
down_revision = 'cb1abef0475f'   
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'requests',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('status_code', sa.Integer, nullable=False),
        sa.Column('response_time', sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()'))
    )
    op.create_index("ix_requests_user_id", "requests", ["user_id"], unique=False)

def downgrade() -> None:
    op.drop_index("ix_requests_user_id", table_name="requests")
    op.drop_table('requests')
