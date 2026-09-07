# -*- coding: utf-8 -*-
"""
Базовий клас SQLAlchemy для Star Agents.
Цей файл використовується як єдиний джерело декларативної бази (Base),
щоб уникнути циклічних імпортів між моделями та core/database.
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData


# ============================================================
# Налаштування метаданих
# ============================================================
# Додаємо префікси для уникнення конфліктів імен у БД
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)


# ============================================================
# Базовий клас для всіх моделей
# ============================================================
class Base(DeclarativeBase):
    """Базовий клас для всіх моделей Star Agents"""
    metadata = metadata

    # Автоматичне генерування __tablename__ якщо не задано
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def to_dict(self, include_relationships: bool = False) -> dict:
        """
        Конвертує модель у словник.
        :param include_relationships: чи включати зв’язки (relationship)
        """
        data = {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
        if include_relationships:
            for rel in self.__mapper__.relationships:
                value = getattr(self, rel.key)
                if value is None:
                    data[rel.key] = None
                elif isinstance(value, list):
                    data[rel.key] = [v.to_dict() for v in value]
                else:
                    data[rel.key] = value.to_dict()
        return data

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"
