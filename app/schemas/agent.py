from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Базова схема — спільні поля
class AgentBase(BaseModel):
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    skills: Optional[str] = None
    status: Optional[str] = "active"   # у моделі це TEXT/VARCHAR
    price: Optional[float] = 0.0       # у моделі є поле price


# Створення агента
class AgentCreate(AgentBase):
    name: str


# Оновлення агента
class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    skills: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = None


# Відповідь API
class AgentRead(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
