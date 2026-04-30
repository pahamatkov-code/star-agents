from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Основні поля
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True)

    # Баланс користувача
    balance = Column(Integer, default=0, nullable=False)

    # Таймстемпи
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Зв’язки
    purchases = relationship(
        "Purchase",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    balance_transactions = relationship(
        "BalanceTransaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# 🔥 ВАЖЛИВО: імпортуємо залежні моделі ПІСЛЯ визначення User
from app.models.purchase import Purchase
from app.models.balance_transaction import BalanceTransaction
