from pydantic import BaseModel
from typing import List, Optional


# -----------------------------
# DAILY METRICS (для графіків)
# -----------------------------
class DailyCountRevenue(BaseModel):
    day: str
    count: Optional[int] = None
    revenue: Optional[float] = None


class DailyAmount(BaseModel):
    day: str
    amount: float


# -----------------------------
# TOP LISTS
# -----------------------------
class TopAgent(BaseModel):
    agent: str
    count: int
    revenue: float


class TopUser(BaseModel):
    user: str
    count: int
    spent: float


# -----------------------------
# PURCHASE ANALYTICS
# -----------------------------
class PurchaseAnalytics(BaseModel):
    total_purchases: int
    total_revenue: float
    unique_users: int

    purchases_by_day: List[DailyCountRevenue]
    top_agents: List[TopAgent]
    top_users: List[TopUser]


# -----------------------------
# BALANCE ANALYTICS
# -----------------------------
class BalanceAnalytics(BaseModel):
    total_topups: float
    total_spent: float
    net_flow: float

    topups_by_day: List[DailyAmount]
    expenses_by_day: List[DailyAmount]


# -----------------------------
# DASHBOARD RESPONSE
# -----------------------------
class AnalyticsResponse(BaseModel):
    purchases: PurchaseAnalytics
    balance: BalanceAnalytics
