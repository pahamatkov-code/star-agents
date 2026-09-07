# -*- coding: utf-8 -*-
"""
Модель фінансових транзакцій користувачів для Star Agents — ПРОФЕСІЙНА ФІНАЛЬНА ВЕРСІЯ.

Використовується для обліку депозитів, зняття коштів та покупок.
Забезпечує прозорість фінансових операцій і аналітику руху коштів.
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum, func, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    PURCHASE = "purchase"


class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"

    # ============================================================
    # ОСНОВНІ ПОЛЯ
    # ============================================================
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ============================================================
    # ЗВ’ЯЗКИ
    # ============================================================
    user = relationship("User", back_populates="balance_transactions")

    # ============================================================
    # ІНДЕКСИ
    # ============================================================
    __table_args__ = (
        Index("ix_balancetransaction_user_type", "user_id", "type"),
        Index("ix_balancetransaction_created_at", "created_at"),
    )

    # ============================================================
    # МЕТОДИ КОНВЕРТАЦІЇ
    # ============================================================
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "type": self.type.value if self.type else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    # ============================================================
    # РЕПРЕЗЕНТАЦІЯ
    # ============================================================
    def __repr__(self) -> str:
        return (
            f"<BalanceTransaction(id={self.id}, user_id={self.user_id}, "
            f"amount={self.amount}, type={self.type}, created_at={self.created_at})>"
        )

    def __str__(self) -> str:
        return f"{self.type.value.capitalize()} of {self.amount} by user {self.user_id}"


__all__ = ["BalanceTransaction", "TransactionType"]
