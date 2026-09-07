# -*- coding: utf-8 -*-
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    """Базова схема користувача"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    role: str = "user"


class UserCreate(UserBase):
    """Схема для створення користувача"""
    password: str = Field(..., min_length=6)


class UserRead(UserBase):
    """Схема для читання користувача"""
    id: int
    balance: float = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Схема для оновлення користувача"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None
    role: Optional[str] = None


# ============================================================
# 🔴 ВАЖЛИВО! ДОДАЙТЕ ЦЕЙ КЛАС
# ============================================================
class UserList(BaseModel):
    """Схема для списку користувачів з пагінацією"""
    users: List[UserRead]
    total: int
    skip: int
    limit: int
    
    class Config:
        from_attributes = True