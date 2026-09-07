# -*- coding: utf-8 -*-
"""
Схеми для аналітики Star Agents - МАКСИМАЛЬНО ПРОДУКТИВНА ФІНАЛЬНА ВЕРСІЯ 3.0.0
Оптимізовано для швидкості, з мінімальними залежностями
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# ============================================================
# БАЗОВА СХЕМА - ОПТИМІЗОВАНА
# ============================================================
class BaseAnalyticsModel(BaseModel):
    """Базова схема з оптимізованими налаштуваннями"""
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        frozen=False,  # Дозволяє редагування
        str_strip_whitespace=True,  # Автоматично обрізає пробіли
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


# ============================================================
# ОСНОВНІ СХЕМИ - МІНІМАЛІСТИЧНІ
# ============================================================
class TopAgentItem(BaseModel):
    """ТОП агентів"""
    agent: str = Field(..., min_length=1, max_length=100)
    count: int = Field(0, ge=0)
    revenue: float = Field(0.0, ge=0.0)


class TopUserItem(BaseModel):
    """ТОП користувачів"""
    user: str = Field(..., min_length=1, max_length=255)
    count: int = Field(0, ge=0)
    spent: float = Field(0.0, ge=0.0)


# ============================================================
# СХЕМИ ДЛЯ ЧАСОВИХ РЯДІВ
# ============================================================
class DailyCountRevenue(BaseModel):
    """Щоденна статистика"""
    day: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    count: int = Field(0, ge=0)
    revenue: float = Field(0.0, ge=0.0)


class DailyAmount(BaseModel):
    """Щоденна сума"""
    day: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    amount: float = Field(0.0)


# ============================================================
# РОЗШИРЕНА СТАТИСТИКА - ОПЦІОНАЛЬНА
# ============================================================
class PurchaseAnalytics(BaseModel):
    """Аналітика покупок"""
    total_purchases: int = 0
    total_revenue: float = 0.0
    unique_users: int = 0
    purchases_by_day: List[DailyCountRevenue] = []
    top_agents: List[TopAgentItem] = []
    top_users: List[TopUserItem] = []


class BalanceAnalytics(BaseModel):
    """Аналітика балансу"""
    total_topups: float = 0.0
    total_spent: float = 0.0
    net_flow: float = 0.0
    topups_by_day: List[DailyAmount] = []
    expenses_by_day: List[DailyAmount] = []


class IntentData(BaseModel):
    """Дані про інтент"""
    count: int = 0
    color: str = "#6366F1"
    percentage: Optional[float] = None


class RecentMessage(BaseModel):
    """Останнє повідомлення"""
    message: str = ""
    time: str = ""
    datetime: Optional[str] = None
    user_id: Optional[int] = None
    intent: Optional[str] = None
    status: str = "success"


class AnalyticsMeta(BaseModel):
    """Метадані відповіді"""
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    user: str = "system"
    cache: str = "fresh"
    version: str = "3.0.0"


# ============================================================
# ГОЛОВНА ВІДПОВІДЬ - ОПТИМІЗОВАНА
# ============================================================
class AnalyticsResponse(BaseModel):
    """
    Оптимізована відповідь для дашборду
    """
    # Базові метрики (обов'язкові)
    requests: int = 0
    avg_time: float = 0.0
    errors: int = 0
    users: int = 0
    revenue: float = 0.0
    
    # Інтенти (опціональні)
    intents: Dict[str, int] = {}
    intents_distribution: Optional[Dict[str, int]] = None
    intents_colors: Optional[Dict[str, IntentData]] = None
    
    # ТОПи (опціональні)
    top_agents: List[TopAgentItem] = []
    top_users: List[TopUserItem] = []
    
    # Розширена аналітика (опціональна)
    purchases: Optional[PurchaseAnalytics] = None
    balance: Optional[BalanceAnalytics] = None
    
    # Динаміка (опціональна)
    timeline: List[Dict[str, Any]] = []
    realtime: Optional[Dict[str, Any]] = None
    
    # Повідомлення (опціональні)
    recent_messages: List[RecentMessage] = []
    
    # Додаткові метрики (опціональні)
    performance: Optional[Dict[str, Any]] = None
    engagement: Optional[Dict[str, Any]] = None
    system_health: Optional[Dict[str, Any]] = None
    
    # Метадані (без підкреслення!)
    meta: Optional[AnalyticsMeta] = None
    
    # Додаткові дані
    details: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        extra="allow",
        json_schema_extra={
            "example": {
                "requests": 150,
                "avg_time": 0.45,
                "errors": 3,
                "users": 45,
                "revenue": 1250.50,
                "intents": {"support": 80, "sales": 45},
                "top_agents": [{"agent": "Agent-1", "count": 60, "revenue": 500.0}],
                "meta": {
                    "generated_at": "2026-08-22T16:30:00",
                    "user": "admin",
                    "cache": "fresh",
                    "version": "3.0.0"
                }
            }
        }
    )


# ============================================================
# СХЕМИ ДЛЯ ЗАПИТІВ
# ============================================================
class AnalyticsQueryParams(BaseModel):
    """Параметри запиту для аналітики"""
    hours: Optional[int] = Field(24, ge=1, le=168)
    days: Optional[int] = Field(7, ge=1, le=30)
    refresh: bool = False
    limit: Optional[int] = Field(10, ge=1, le=50)


# ============================================================
# ЕКСПОРТ - ОПТИМІЗОВАНИЙ
# ============================================================
__all__ = [
    "BaseAnalyticsModel",
    "TopAgentItem",
    "TopUserItem",
    "DailyCountRevenue",
    "DailyAmount",
    "PurchaseAnalytics",
    "BalanceAnalytics",
    "IntentData",
    "RecentMessage",
    "AnalyticsMeta",
    "AnalyticsResponse",
    "AnalyticsQueryParams",
]