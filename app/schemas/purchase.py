from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Базові поля покупки
class PurchaseBase(BaseModel):
    agent_id: int
    price: float


# Створення покупки
class PurchaseCreate(PurchaseBase):
    # User не передає user_id — беремо з JWT
    # Admin може передати user_id вручну
    user_id: Optional[int] = None


# Оновлення покупки (тільки admin)
class PurchaseUpdate(BaseModel):
    agent_id: Optional[int] = None
    price: Optional[float] = None


# Відповідь API
class PurchaseRead(PurchaseBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Додаткова схема для списків (якщо потрібно)
class PurchaseData(BaseModel):
    id: int
    agent_id: int
    price: float
    created_at: datetime
    agent_name: Optional[str] = None
    agent_role: Optional[str] = None
