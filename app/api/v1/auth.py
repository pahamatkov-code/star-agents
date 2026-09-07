# -*- coding: utf-8 -*-
"""
Аутентифікація та авторизація для Star Agents - ФІНАЛЬНА ВЕРСІЯ

Цей модуль відповідає за:
- Реєстрацію нових користувачів
- Вхід в систему (логін)
- Оновлення токенів (refresh)
- Вихід з системи (logout)
- Перевірку токенів
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenPair, RefreshRequest, UserRegister
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
)
from app.services.user_service import UserService
from app.models.user import User

# ============================================================
# РОУТЕР - БЕЗ ПРЕФІКСУ (префікс додається в main.py)
# ============================================================
router = APIRouter(tags=["Authentication"])


# ============================================================
# REGISTER - Реєстрація нового користувача
# ============================================================
@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_user(
    data: UserRegister,  # або LoginRequest
    db: Session = Depends(get_db)
):
    """
    Реєстрація нового користувача.
    
    Args:
        data: Email та пароль користувача
        db: Сесія бази даних
    
    Returns:
        dict: Повідомлення про успішну реєстрацію та ID користувача
    """
    user_service = UserService(db)

    # Перевіряємо чи існує користувач з таким email
    existing = user_service.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Хешуємо пароль
    hashed_password = get_password_hash(data.password)
    
    # Створюємо користувача
    user = user_service.create_user(
        email=data.email,
        hashed_password=hashed_password,
        full_name=getattr(data, 'full_name', None),
        role="user",
    )

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email
    }


# ============================================================
# LOGIN - Вхід в систему
# ============================================================
@router.post("/login", response_model=TokenPair)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Вхід в систему з отриманням токенів.
    
    Args:
        form_data: Email (username) та пароль
        db: Сесія бази даних
    
    Returns:
        TokenPair: Access та Refresh токени
    """
    user_service = UserService(db)

    # Шукаємо користувача за email
    user = user_service.get_by_email(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Перевіряємо пароль
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Перевіряємо чи активний користувач
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Створюємо токени
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# ============================================================
# REFRESH - Оновлення токенів
# ============================================================
@router.post("/refresh", response_model=TokenPair)
def refresh_token(
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Оновлення access токена за допомогою refresh токена.
    
    Args:
        data: Refresh токен
        db: Сесія бази даних
    
    Returns:
        TokenPair: Нові Access та Refresh токени
    """
    # Декодуємо refresh токен
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Отримуємо ID користувача
    user_id = int(payload.get("sub"))
    role = payload.get("role")

    user_service = UserService(db)
    user = user_service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Перевіряємо чи активний користувач
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Створюємо нові токени
    new_access = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    new_refresh = create_refresh_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return TokenPair(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
    )


# ============================================================
# LOGOUT - Вихід з системи (опціонально)
# ============================================================
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    """
    Вихід з системи.
    На стороні клієнта потрібно просто видалити токени.
    """
    # Тут можна додати чорний список токенів, якщо потрібно
    return None


# ============================================================
# ME - Отримати інформацію про поточного користувача
# ============================================================
@router.get("/me")
def get_current_user_info(
    db: Session = Depends(get_db),
    token: Optional[str] = None
):
    """
    Отримати інформацію про поточного користувача за токеном.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required",
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user_id = int(payload.get("sub"))
    user_service = UserService(db)
    user = user_service.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
    }


# ============================================================
# ЕКСПОРТИ
# ============================================================
__all__ = [
    "router",
]