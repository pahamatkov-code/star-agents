# -*- coding: utf-8 -*-
"""
Модель повідомлень чату — ФІНАЛЬНА ПРОФЕСІЙНА ВЕРСІЯ
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Numeric, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base


class ChatStatus(str, enum.Enum):
    OK = "ok"
    ERROR = "error"
    PENDING = "pending"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    # ============================================================
    # ОСНОВНІ ПОЛЯ
    # ============================================================
    id = Column(Integer, primary_key=True, index=True)

    # 👤 Foreign Key → User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # ============================================================
    # ЗМІСТ ПОВІДОМЛЕННЯ
    # ============================================================
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)

    # ============================================================
    # МЕТАДАНІ
    # ============================================================
    intent = Column(String(100), nullable=True, index=True)
    status = Column(Enum(ChatStatus), default=ChatStatus.OK, nullable=False, index=True)
    response_time = Column(Numeric(12, 2), default=0.00, nullable=False)  # Час відповіді в мс
    is_processed = Column(Boolean, default=True, nullable=False)

    # ============================================================
    # ЧАСОВІ МІТКИ
    # ============================================================
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ============================================================
    # ЗВ’ЯЗКИ
    # ============================================================
    user = relationship("User", back_populates="messages")

    # ============================================================
    # МЕТОДИ
    # ============================================================
    def to_dict(self) -> dict:
        """Конвертувати повідомлення в словник"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "response": self.response,
            "intent": self.intent,
            "status": self.status.value if self.status else None,
            "response_time": float(self.response_time) if self.response_time is not None else None,
            "is_processed": self.is_processed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def mark_processed(self, status: ChatStatus = ChatStatus.OK, response_time: float = 0.0) -> None:
        """Позначити повідомлення як оброблене"""
        self.is_processed = True
        self.status = status
        self.response_time = response_time
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} user_id={self.user_id} intent={self.intent} status={self.status}>"

    def __str__(self) -> str:
        return f"ChatMessage #{self.id}: {self.message[:50]}..."


__all__ = ["ChatMessage", "ChatStatus"]
