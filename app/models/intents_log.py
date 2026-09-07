# -*- coding: utf-8 -*-
"""
Модель логів інтентів для Star Agents — ФІНАЛЬНА ПРОФЕСІЙНА ВЕРСІЯ.

Зберігає всі визначені наміри (intents) користувачів для аналітики,
включаючи повідомлення, рівень впевненості та час створення.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class IntentsLog(Base):
    __tablename__ = "intents_log"

    # ============================================================
    # ОСНОВНІ ПОЛЯ
    # ============================================================
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    intent = Column(String(100), nullable=False, index=True)
    confidence = Column(Integer, nullable=False)  # рівень впевненості (0–100)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ============================================================
    # ЗВ’ЯЗКИ
    # ============================================================
    user = relationship("User", back_populates="intents_log")

    # ============================================================
    # ІНДЕКСИ
    # ============================================================
    __table_args__ = (
        Index("ix_intentslog_user_intent", "user_id", "intent"),
        Index("ix_intentslog_created_at", "created_at"),
    )

    # ============================================================
    # МЕТОДИ КОНВЕРТАЦІЇ
    # ============================================================
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "intent": self.intent,
            "confidence": self.confidence,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    # ============================================================
    # АНАЛІТИКА
    # ============================================================
    @staticmethod
    def top_intents(session, limit: int = 5):
        """Отримати топ-N інтентів за кількістю"""
        return (
            session.query(IntentsLog.intent, func.count(IntentsLog.id).label("count"))
            .group_by(IntentsLog.intent)
            .order_by(func.count(IntentsLog.id).desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def average_confidence(session):
        """Середній рівень впевненості по всіх інтентах"""
        return session.query(func.avg(IntentsLog.confidence)).scalar() or 0.0

    # ============================================================
    # РЕПРЕЗЕНТАЦІЯ
    # ============================================================
    def __repr__(self) -> str:
        return f"<IntentsLog(id={self.id}, user_id={self.user_id}, intent={self.intent}, confidence={self.confidence})>"

    def __str__(self) -> str:
        return f"Intent '{self.intent}' (confidence={self.confidence}%) from user {self.user_id}"


__all__ = ["IntentsLog"]
