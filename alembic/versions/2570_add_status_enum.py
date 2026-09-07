from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2570_add_status_enum'
down_revision: str = '256909db0ec4'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Створюємо ENUM для status
    status_enum = sa.Enum("active", "inactive", "suspended", name="status_enum")
    status_enum.create(op.get_bind(), checkfirst=True)

    # Переводимо колонку status у ENUM
    op.execute("ALTER TABLE agents ALTER COLUMN status TYPE status_enum USING status::text::status_enum")

    # Додаємо дефолт
    op.execute("ALTER TABLE agents ALTER COLUMN status SET DEFAULT 'active'")


def downgrade() -> None:
    # Повертаємо status у varchar
    op.execute("ALTER TABLE agents ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE agents ALTER COLUMN status TYPE varchar")

    # Видаляємо ENUM
    op.execute("DROP TYPE IF EXISTS status_enum")
