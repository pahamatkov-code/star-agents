# -*- coding: utf-8 -*-
"""
Залежності для FastAPI - ФІНАЛЬНА ПОКРАЩЕНА ВЕРСІЯ

Цей модуль містить всі Dependency Injection функції для:
- Отримання сесії бази даних
- Аутентифікації та авторизації
- Перевірки ролей та прав
- Валідації токенів
- Кешування користувачів
- Логування дій
"""
from typing import Optional, Callable, List
from functools import wraps
import logging

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, ExpiredSignatureError

from app.core.database import get_db
from app.models.user import User
from app.core.config import settings
from app.core.cache import cache
from app.core.security import verify_token

logger = logging.getLogger("star_agents")

# ============================================================
# OAUTH2 СХЕМА
# ============================================================
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=True,
    description="JWT токен для авторизації"
)


# ============================================================
# ОТРИМАННЯ ПОТОЧНОГО КОРИСТУВАЧА
# ============================================================
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    request: Optional[Request] = None
) -> User:
    """
    Отримує поточного користувача з JWT токена.
    """
    # 1. Перевіряємо кеш
    cache_key = f"user_token_{token[:20]}"
    cached_user = cache.get(cache_key)
    if cached_user:
        logger.debug(f"✅ User from cache: {cached_user.email}")
        return cached_user
    
    try:
        # 2. Верифікуємо токен
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 3. Отримуємо user_id з payload
        user_id: Optional[int] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 4. Перевіряємо тип токена
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Use access token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 5. Отримуємо користувача з бази
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 6. Перевіряємо, чи активний користувач
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 7. Зберігаємо в кеш
        cache.set(cache_key, user, ttl=60)
        
        # 8. Оновлюємо час останньої активності
        try:
            from datetime import datetime
            user.last_active = datetime.utcnow()
            db.commit()
        except Exception as e:
            logger.warning(f"Could not update last_active: {e}")
            db.rollback()
        
        # 9. Логуємо успішну авторизацію
        ip = request.client.host if request and request.client else "unknown"
        logger.info(f"🔐 User authenticated: {user.email} from {ip}")
        
        return user
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning(f"JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
        )


# ============================================================
# ПЕРЕВІРКА РОЛІ
# ============================================================
def require_role(required_role: str) -> Callable:
    """Фабрика залежності для перевірки ролі користувача."""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role != required_role:
            logger.warning(f"Access denied for {user.email}. Required: {required_role}, got: {user.role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}",
            )
        return user
    return role_checker


def require_any_role(allowed_roles: List[str]) -> Callable:
    """Перевіряє, чи має користувач одну з дозволених ролей."""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            logger.warning(f"Access denied for {user.email}. Allowed: {allowed_roles}, got: {user.role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Allowed roles: {', '.join(allowed_roles)}",
            )
        return user
    return role_checker


# ============================================================
# СПЕЦІАЛІЗОВАНІ ПЕРЕВІРКИ
# ============================================================
def require_admin(user: User = Depends(require_role("admin"))) -> User:
    """Спеціалізована залежність для адміністраторів."""
    return user


def require_manager(user: User = Depends(require_role("manager"))) -> User:
    """Спеціалізована залежність для менеджерів."""
    return user


def require_admin_or_manager(
    user: User = Depends(require_any_role(["admin", "manager"]))
) -> User:
    """Спеціалізована залежність для адміністраторів та менеджерів."""
    return user


# ============================================================
# ОПЦІОНАЛЬНА АВТОРИЗАЦІЯ
# ============================================================
async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Отримує поточного користувача, але не викликає помилку, якщо токен відсутній."""
    if not token:
        return None
    
    try:
        return await get_current_user(token, db)
    except HTTPException as e:
        if e.status_code in [401, 403]:
            return None
        raise


# ============================================================
# ПЕРЕВІРКИ СТАНУ КОРИСТУВАЧА
# ============================================================
async def get_active_user(user: User = Depends(get_current_user)) -> User:
    """Перевіряє, що користувач активний."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return user


async def require_positive_balance(user: User = Depends(get_current_user)) -> User:
    """Перевіряє, що користувач має позитивний баланс."""
    if hasattr(user, 'balance') and user.balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient balance. Please top up your account.",
        )
    return user


async def require_analytics_access(user: User = Depends(get_current_user)) -> User:
    """Перевіряє, що користувач має доступ до аналітики."""
    allowed_roles = ["admin", "manager", "analyst"]
    if user.role in allowed_roles:
        return user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied. Analytics is available only for admin, managers and analysts.",
    )


# ============================================================
# ЕКСПОРТИ
# ============================================================
__all__ = [
    "oauth2_scheme",
    "get_current_user",
    "get_current_user_optional",
    "require_role",
    "require_any_role",
    "require_admin",
    "require_manager",
    "require_admin_or_manager",
    "get_active_user",
    "require_positive_balance",
    "require_analytics_access",
]