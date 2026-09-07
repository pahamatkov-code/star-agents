# -*- coding: utf-8 -*-
"""
Фінальний файл імпорту моделей для реєстрації у Base.

SQLAlchemy бачить усі таблиці та зв’язки тільки якщо вони імпортовані тут.
Цей файл гарантує, що Alembic зможе коректно автогенерувати міграції.
"""

from app.db.base_class import Base

# ============================================================
# ІМПОРТИ МОДЕЛЕЙ
# ============================================================
from app.models.user import User, UserRole, UserStatus
from app.models.agent import Agent
from app.models.chat import ChatMessage
from app.models.intents_log import IntentsLog
from app.models.purchase import Purchase
from app.models.balance_transaction import BalanceTransaction, TransactionType
from app.models.request import Request

# ============================================================
# ЕКСПОРТИ
# ============================================================
__all__ = [
    "Base",
    "User",
    "UserRole",
    "UserStatus",
    "Agent",
    "ChatMessage",
    "IntentsLog",
    "Purchase",
    "BalanceTransaction",
    "TransactionType",
    "Request",
]
