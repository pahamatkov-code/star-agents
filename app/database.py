# -*- coding: utf-8 -*-
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Отримуємо URL зі змінних оточення, або використовуємо PostgreSQL за замовчуванням
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/star_agents"
)

# Налаштування підключення до бази даних
engine = create_engine(
    DATABASE_URL,
    pool_size=10,              # Розмір пулу з'єднань
    max_overflow=20,           # Максимум додаткових з'єднань
    pool_pre_ping=True,        # Перевірка з'єднання перед використанням
    pool_recycle=3600,         # Перепідключення кожну годину
    echo=False                 # Логування SQL (False у продакшені)
)

# Фабрика сесій
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовий клас для моделей
Base = declarative_base()

# Dependency для отримання сесії бази даних
def get_db():
    """
    Генератор для отримання сесії бази даних.
    Використовується як FastAPI Dependency.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()