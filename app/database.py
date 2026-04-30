from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL для підключення до бази (SQLite для прикладу)
SQLALCHEMY_DATABASE_URL = "sqlite:///./agents.db"

# Якщо використовуєш PostgreSQL або MySQL, заміни на відповідний URL
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Використовуємо сучасний імпорт declarative_base з sqlalchemy.orm
Base = declarative_base()

# Dependency для отримання сесії
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
