# -*- coding: utf-8 -*-
"""
Модель покупок користувачів для Star Agents — ПРОФЕСІЙНА ФІНАЛЬНА ВЕРСІЯ.

Зберігає всі транзакції покупок, включаючи назву товару/послуги,
суму та час створення. Використовується для аналітики та фінансових звітів.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Purchase(Base):
    __tablename__ = "purchases"

    # ============================================================
    # ОСНОВНІ ПОЛЯ
    # ============================================================
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    item_name = Column(String(255), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # сума покупки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ============================================================
    # ЗВ’ЯЗКИ
    # ============================================================
    user = relationship("User", back_populates="purchases")

    # ============================================================
    # ІНДЕКСИ
    # ============================================================
    __table_args__ = (
        Index("ix_purchase_user_item", "user_id", "item_name"),
        Index("ix_purchase_created_at", "created_at"),
    )

    # ============================================================
    # МЕТОДИ КОНВЕРТАЦІЇ
    # ============================================================
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_name": self.item_name,
            "amount": self.amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    # ============================================================
    # РЕПРЕЗЕНТАЦІЯ
    # ============================================================
    def __repr__(self) -> str:
        return f"<Purchase(id={self.id}, user_id={self.user_id}, item_name={self.item_name}, amount={self.amount})>"

    def __str__(self) -> str:
        return f"Purchase '{self.item_name}' for {self.amount} by user {self.user_id}"


__all__ = ["Purchase"]
