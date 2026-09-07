from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2572_cleanup_chat_messages'
down_revision: str = '2570_add_status_enum'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # ENUM для status
    status_enum = sa.Enum("ok", "error", "pending", name="chat_status_enum")
    status_enum.create(op.get_bind(), checkfirst=True)

    # Спочатку прибираємо default
    op.execute("ALTER TABLE chat_messages ALTER COLUMN status DROP DEFAULT")

    # Міняємо тип на ENUM
    op.execute("ALTER TABLE chat_messages ALTER COLUMN status TYPE chat_status_enum USING status::text::chat_status_enum")

    # Встановлюємо новий default
    op.execute("ALTER TABLE chat_messages ALTER COLUMN status SET DEFAULT 'ok'")

    # Переводимо response_time у numeric
    op.execute("ALTER TABLE chat_messages ALTER COLUMN response_time TYPE numeric(12,2) USING response_time::numeric")
    op.execute("ALTER TABLE chat_messages ALTER COLUMN response_time SET DEFAULT 0.00")

    # Додаємо індекс по agent_id
    op.create_index("ix_chat_messages_agent_id", "chat_messages", ["agent_id"], unique=False)

