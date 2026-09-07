# -*- coding: utf-8 -*-
"""
Схеми для аутентифікації - ФІНАЛЬНА ВЕРСІЯ
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Запит на вхід"""
    email: EmailStr = Field(..., description="Email користувача")
    password: str = Field(..., min_length=6, description="Пароль")


class UserRegister(BaseModel):
    """Схема для реєстрації користувача"""
    email: EmailStr = Field(..., description="Email користувача")
    password: str = Field(..., min_length=6, description="Пароль")
    full_name: Optional[str] = Field(None, description="Повне ім'я")
    role: Optional[str] = Field("user", description="Роль")


class TokenPair(BaseModel):
    """Пара токенів"""
    access_token: str = Field(..., description="Access токен")
    refresh_token: str = Field(..., description="Refresh токен")
    token_type: str = Field("bearer", description="Тип токена")


class RefreshRequest(BaseModel):
    """Запит на оновлення токена"""
    refresh_token: str = Field(..., description="Refresh токен")


class TokenData(BaseModel):
    """Дані з токена"""
    user_id: int
    role: str
    exp: Optional[int] = None


class AuthResponse(BaseModel):
    """Відповідь аутентифікації"""
    access_token: str
    token_type: str = "bearer"