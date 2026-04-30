from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BalanceTransactionBase(BaseModel):
    amount: float
    type: str  # "topup", "purchase", "refund", "adjustment"


class BalanceTransactionCreate(BalanceTransactionBase):
    user_id: int  # admin може створювати транзакції вручну


class BalanceTransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[str] = None


class BalanceTransactionRead(BalanceTransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
