"""init models

Revision ID: 20260819_init_models
Revises: 
Create Date: 2026-08-19 15:20:00
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = '20260819_init_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # === USERS ===
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('telegram_id', sa.BigInteger(), unique=True, index=True),
        sa.Column('email', sa.String(255), unique=True, index=True),
        sa.Column('username', sa.String(100), index=True),
        sa.Column('hashed_password', sa.String(255)),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verification_token', sa.String(255)),
        sa.Column('full_name', sa.String(255)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('phone_number', sa.String(20)),
        sa.Column('bio', sa.Text()),
        sa.Column('role', sa.String(50), default="user"),
        sa.Column('status', sa.String(20), default="active"),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('balance', sa.Float(), default=0.0),
        sa.Column('total_spent', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('last_active', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('preferences', sa.Text())
    )

    # === AGENTS ===
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text())
    )

    # === CHAT MESSAGES ===
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('response', sa.Text()),
        sa.Column('intent', sa.String(100)),
        sa.Column('status', sa.String(50), default="ok"),
        sa.Column('response_time', sa.Float()),
        sa.Column('is_processed', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )

    # === PURCHASES ===
    op.create_table(
        'purchases',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id', ondelete="CASCADE"), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now())
    )

    # === BALANCE TRANSACTIONS ===
    op.create_table(
        'balance_transactions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now())
    )

    # === INTENTS LOG ===
    op.create_table(
        'intents_log',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
        sa.Column('intent', sa.String(255), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now())
    )

    # === REQUESTS ===
    op.create_table(
        'requests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
        sa.Column('endpoint', sa.String(255), nullable=False),
        sa.Column('payload', sa.Text()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now())
    )


def downgrade():
    op.drop_table('requests')
    op.drop_table('intents_log')
    op.drop_table('balance_transactions')
    op.drop_table('purchases')
    op.drop_table('chat_messages')
    op.drop_table('agents')
    op.drop_table('users')
