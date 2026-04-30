from pydantic import BaseModel


class BalanceTopUpRequest(BaseModel):
    user_id: int
    amount: float


class BalanceResponse(BaseModel):
    user_id: int
    balance: float
