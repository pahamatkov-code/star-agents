# -*- coding: utf-8 -*-
"""
Налаштування бази даних Star Agents — ПРОФЕСІЙНА ФІНАЛЬНА ВЕРСІЯ.

✔ Використовує SQLAlchemy + psycopg2 для PostgreSQL.
✔ Має оптимальні параметри пулу з'єднань.
✔ Уникає циклічних імпортів.
✔ Містить утиліти для роботи з БД (init, drop, get_db).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator
from app.core.config import settings

# ============================================================
# БАЗОВИЙ КЛАС ДЛЯ МОДЕЛЕЙ
# ============================================================
Base = declarative_base()

# ============================================================
# ENGINE — ПІДКЛЮЧЕННЯ ДО POSTGRES
# ============================================================
engine = create_engine(
    settings.DATABASE_URL,          # "postgresql://postgres:postgres@db:5432/star_agents"
    pool_pre_ping=True,             # перевірка з'єднання перед використанням
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO           # логування SQL (True тільки для debug)
)

# ============================================================
# СЕСІЯ БАЗИ ДАНИХ
# ============================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================================
# DEPENDENCY ДЛЯ FASTAPI
# ============================================================
def get_db() -> Generator[Session, None, None]:
    """
    Dependency для отримання сесії бази даних.
    Використовується в ендпоінтах FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# ДОПОМІЖНІ ФУНКЦІЇ
# ============================================================
def init_db() -> None:
    """
    Створює всі таблиці в базі даних (якщо їх немає).
    Викликається при старті додатку.
    """
    import app.db.base  # імпортує всі моделі через base.py
    Base.metadata.create_all(bind=engine)

def drop_db() -> None:
    """
    Видаляє всі таблиці з бази даних.
    ⚠️ ТІЛЬКИ ДЛЯ РОЗРОБКИ! НЕ ВИКОРИСТОВУЙТЕ В ПРОДАКШНІ!
    """
    Base.metadata.drop_all(bind=engine)

def get_base() -> declarative_base:
    """
    Повертає базовий клас для моделей.
    """
    return Base

# ============================================================
# ЕКСПОРТИ
# ============================================================
__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "drop_db",
    "get_base",
]
