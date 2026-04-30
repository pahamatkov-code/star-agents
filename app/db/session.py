from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Створюємо engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Створюємо фабрику сесій
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Головна функція get_db, яку імпортує auth.py
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
