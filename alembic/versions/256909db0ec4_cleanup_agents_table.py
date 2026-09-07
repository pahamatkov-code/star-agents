from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '256909db0ec4'
down_revision: str = 'e6d4f7ea7a26'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Видаляємо дублікати колонок (без status!)
    for col in ["email", "department", "skills", "model", "is_active"]:
        try:
            op.drop_column("agents", col)
        except Exception:
            pass

    # ENUM для role
    role_enum = sa.Enum("agent", "assistant", "system", name="role_enum")
    role_enum.create(op.get_bind(), checkfirst=True)

    # Прибираємо дефолт перед зміною типу
    op.execute("ALTER TABLE agents ALTER COLUMN role DROP DEFAULT")

    # Міняємо тип role на ENUM
    op.execute("ALTER TABLE agents ALTER COLUMN role TYPE role_enum USING role::text::role_enum")

    # Додаємо дефолт після конверсії
    op.execute("ALTER TABLE agents ALTER COLUMN role SET DEFAULT 'agent'")

    # Фінансові поля
    op.execute("ALTER TABLE agents ALTER COLUMN price TYPE numeric(12,2) USING price::numeric")
    op.execute("ALTER TABLE agents ALTER COLUMN price_per_request TYPE numeric(12,2) USING price_per_request::numeric")

    # Додаємо дефолти для числових полів
    op.execute("ALTER TABLE agents ALTER COLUMN price SET DEFAULT 0.00")
    op.execute("ALTER TABLE agents ALTER COLUMN price_per_request SET DEFAULT 0.00")


def downgrade() -> None:
    # Повертаємо числові поля у float8
    op.execute("ALTER TABLE agents ALTER COLUMN price DROP DEFAULT")
    op.execute("ALTER TABLE agents ALTER COLUMN price_per_request DROP DEFAULT")
    op.execute("ALTER TABLE agents ALTER COLUMN price TYPE double precision")
    op.execute("ALTER TABLE agents ALTER COLUMN price_per_request TYPE double precision")

    # Повертаємо role у varchar
    op.execute("ALTER TABLE agents ALTER COLUMN role DROP DEFAULT")
    op.execute("ALTER TABLE agents ALTER COLUMN role TYPE varchar")

    # Видаляємо ENUM
    op.execute("DROP TYPE IF EXISTS role_enum")
