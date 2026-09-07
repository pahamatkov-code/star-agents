# -*- coding: utf-8 -*-
"""
Схеми Pydantic для агентів - ФІНАЛЬНА ВЕРСІЯ
Повна сумісність з моделлю Agent та всіма ендпоінтами
"""
from typing import Optional, List
from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime


# ============================================================
# БАЗОВА СХЕМА
# ============================================================

class AgentBase(BaseModel):
    """Базова схема агента - спільні поля для всіх операцій"""
    name: str = Field(..., min_length=1, max_length=100, description="Ім'я агента")
    role: Optional[str] = Field(None, max_length=50, description="Роль агента")
    email: Optional[EmailStr] = Field(None, description="Email агента")
    department: Optional[str] = Field(None, max_length=50, description="Відділ")
    skills: Optional[str] = Field(None, description="Навички (текстовий опис)")
    status: Optional[str] = Field("active", description="Статус (active/inactive)")
    price: Optional[float] = Field(0.0, ge=0, description="Ціна за використання")
    
    @validator('name')
    def validate_name(cls, v):
        """Валідація імені"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('status')
    def validate_status(cls, v):
        """Валідація статусу"""
        if v and v not in ['active', 'inactive']:
            raise ValueError('Status must be "active" or "inactive"')
        return v
    
    @validator('price')
    def validate_price(cls, v):
        """Валідація ціни"""
        if v is not None and v < 0:
            raise ValueError('Price cannot be negative')
        return v


# ============================================================
# СТВОРЕННЯ АГЕНТА
# ============================================================

class AgentCreate(AgentBase):
    """Схема для створення агента"""
    name: str = Field(..., min_length=1, max_length=100, description="Ім'я агента (обов'язково)")
    
    # Перевизначаємо поля, щоб зробити їх опціональними
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    skills: Optional[str] = None
    status: Optional[str] = "active"
    price: Optional[float] = 0.0


# ============================================================
# ОНОВЛЕННЯ АГЕНТА
# ============================================================

class AgentUpdate(BaseModel):
    """Схема для оновлення агента - всі поля опціональні"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Ім'я агента")
    role: Optional[str] = Field(None, max_length=50, description="Роль агента")
    email: Optional[EmailStr] = Field(None, description="Email агента")
    department: Optional[str] = Field(None, max_length=50, description="Відділ")
    skills: Optional[str] = Field(None, description="Навички")
    status: Optional[str] = Field(None, description="Статус (active/inactive)")
    price: Optional[float] = Field(None, ge=0, description="Ціна за використання")
    
    @validator('name')
    def validate_name(cls, v):
        """Валідація імені при оновленні"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                raise ValueError('Name cannot be empty')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Валідація статусу при оновленні"""
        if v is not None and v not in ['active', 'inactive']:
            raise ValueError('Status must be "active" or "inactive"')
        return v


# ============================================================
# ЧИТАННЯ АГЕНТА (ВІДПОВІДЬ API)
# ============================================================

class AgentRead(AgentBase):
    """Схема для читання агента - повна інформація з БД"""
    id: int = Field(..., description="ID агента")
    created_at: datetime = Field(..., description="Дата створення")
    updated_at: datetime = Field(..., description="Дата оновлення")
    
    # Додаткові поля для зручності
    total_requests: Optional[int] = Field(0, description="Кількість запитів")
    success_rate: Optional[float] = Field(0.0, description="Відсоток успішних відповідей")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================
# СПИСОК АГЕНТІВ
# ============================================================

class AgentList(BaseModel):
    """Схема для списку агентів з пагінацією"""
    agents: List[AgentRead] = Field(..., description="Список агентів")
    total: int = Field(..., description="Загальна кількість")
    skip: int = Field(0, description="Пропущено записів")
    limit: int = Field(100, description="Ліміт записів на сторінку")
    
    class Config:
        from_attributes = True


# ============================================================
# СТАТИСТИКА АГЕНТІВ
# ============================================================

class AgentStats(BaseModel):
    """Статистика використання агента"""
    agent_id: int = Field(..., description="ID агента")
    agent_name: str = Field(..., description="Ім'я агента")
    total_requests: int = Field(0, description="Всього запитів")
    total_errors: int = Field(0, description="Всього помилок")
    avg_response_time: float = Field(0.0, description="Середній час відповіді")
    success_rate: float = Field(0.0, description="Відсоток успішних відповідей")
    last_used: Optional[datetime] = Field(None, description="Останнє використання")
    top_intents: List[str] = Field(default_factory=list, description="ТОП інтентів")
    
    class Config:
        from_attributes = True


class AgentGlobalStats(BaseModel):
    """Глобальна статистика по всіх агентах"""
    total_agents: int = Field(0, description="Всього агентів")
    active_agents: int = Field(0, description="Активних агентів")
    inactive_agents: int = Field(0, description="Неактивних агентів")
    total_requests: int = Field(0, description="Всього запитів")
    avg_success_rate: float = Field(0.0, description="Середній відсоток успішних відповідей")
    most_popular_agent: Optional[str] = Field(None, description="Найпопулярніший агент")
    least_popular_agent: Optional[str] = Field(None, description="Найменш популярний агент")
    agents_by_status: dict = Field(default_factory=dict, description="Агенти за статусом")
    agents_by_department: dict = Field(default_factory=dict, description="Агенти за відділом")
    
    class Config:
        from_attributes = True


# ============================================================
# ПАРАМЕТРИ ПОШУКУ
# ============================================================

class AgentSearchParams(BaseModel):
    """Параметри для пошуку та фільтрації агентів"""
    search: Optional[str] = Field(None, description="Пошук за назвою, роллю або навичками")
    status: Optional[str] = Field(None, description="Фільтр за статусом (active/inactive)")
    department: Optional[str] = Field(None, description="Фільтр за відділом")
    min_price: Optional[float] = Field(None, ge=0, description="Мінімальна ціна")
    max_price: Optional[float] = Field(None, ge=0, description="Максимальна ціна")
    skip: int = Field(0, ge=0, description="Пропустити N записів")
    limit: int = Field(100, ge=1, le=1000, description="Ліміт записів")
    sort_by: Optional[str] = Field("created_at", description="Поле для сортування")
    sort_order: Optional[str] = Field("desc", description="Порядок сортування (asc/desc)")
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        """Валідація поля сортування"""
        allowed_fields = ['name', 'price', 'status', 'created_at', 'updated_at']
        if v and v not in allowed_fields:
            raise ValueError(f'Sort by must be one of: {", ".join(allowed_fields)}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Валідація порядку сортування"""
        if v and v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


# ============================================================
# ЕКСПОРТИ
# ============================================================

__all__ = [
    "AgentBase",
    "AgentCreate",
    "AgentUpdate",
    "AgentRead",
    "AgentList",
    "AgentStats",
    "AgentGlobalStats",
    "AgentSearchParams",
]