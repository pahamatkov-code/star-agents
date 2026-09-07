# -*- coding: utf-8 -*-
"""
Security utilities for password hashing and JWT tokens.
PRODUCTION-READY VERSION 3.1.0
"""
import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


# ============================================================
# ОСНОВНІ ФУНКЦІЇ (для зворотної сумісності)
# ============================================================

def hash_password(password: str) -> str:
    """Hash plain password using bcrypt."""
    return pwd_context.hash(password)


# Аліас для зворотної сумісності з старим кодом
get_password_hash = hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# ПЕРЕВІРКА СКЛАДНОСТІ ПАРОЛЯ
# ============================================================

def is_password_strong(password: str) -> Tuple[bool, str]:
    """
    Перевірка складності пароля.
    
    Returns:
        (bool, str): (чи валідний, повідомлення про помилку)
    """
    if len(password) < 8:
        return False, "Пароль повинен містити щонайменше 8 символів"
    if not re.search(r"[A-Z]", password):
        return False, "Пароль повинен містити хоча б одну велику літеру"
    if not re.search(r"[a-z]", password):
        return False, "Пароль повинен містити хоча б одну малу літеру"
    if not re.search(r"\d", password):
        return False, "Пароль повинен містити хоча б одну цифру"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Пароль повинен містити хоча б один спеціальний символ"
    return True, ""


def generate_secure_password(length: int = 16) -> str:
    """Генерація надійного пароля."""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# ============================================================
# JWT TOKENS
# ============================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Створення JWT access токена."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16)
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Створення JWT refresh токена."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16)
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ============================================================
# ТОКЕН ХЕЛПЕРИ
# ============================================================

def decode_token(token: str, verify_exp: bool = False) -> Optional[Dict[str, Any]]:
    """Декодування JWT токена (без перевірки за замовчуванням)."""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": verify_exp}
        )
    except JWTError:
        return None


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Повна перевірка JWT токена (сигнатура + термін дії)."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Оновлення access токена через refresh token."""
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return create_access_token({"sub": user_id})


def get_token_payload(token: str) -> Optional[Dict[str, Any]]:
    """Отримати payload з токена (без перевірки терміну дії)."""
    return decode_token(token, verify_exp=True)


def get_token_expiration(token: str) -> Optional[datetime]:
    """Отримати час закінчення токена."""
    payload = decode_token(token)
    exp = payload.get("exp") if payload else None
    return datetime.fromtimestamp(exp) if exp else None


def is_token_expired(token: str) -> bool:
    """Перевірка, чи закінчився термін дії токена."""
    exp = get_token_expiration(token)
    return not exp or exp < datetime.utcnow()


def get_token_type(token: str) -> Optional[str]:
    """Отримати тип токена (access/refresh)."""
    payload = decode_token(token)
    return payload.get("type") if payload else None


def get_token_jti(token: str) -> Optional[str]:
    """Отримати унікальний ID токена."""
    payload = decode_token(token)
    return payload.get("jti") if payload else None


def get_user_id_from_token(token: str) -> Optional[str]:
    """Отримати user_id з токена."""
    payload = verify_token(token)
    return payload.get("sub") if payload else None


def get_username_from_token(token: str) -> Optional[str]:
    """Отримати username з токена."""
    payload = verify_token(token)
    return payload.get("username") if payload else None


# ============================================================
# ВАЛІДАЦІЯ
# ============================================================

def validate_token_type(token: str, expected_type: str) -> bool:
    """Перевірка типу токена."""
    payload = decode_token(token)
    return bool(payload and payload.get("type") == expected_type)


def validate_token_user(token: str, user_id: Union[str, int]) -> bool:
    """Перевірка, чи токен належить конкретному користувачеві."""
    payload = verify_token(token)
    if not payload:
        return False
    token_user_id = payload.get("sub")
    return str(token_user_id) == str(user_id)


# ============================================================
# БЛЕК-ЛИСТ ТОКЕНІВ (для майбутнього використання)
# ============================================================

_token_blacklist: set = set()


def add_to_blacklist(jti: str) -> None:
    """Додати токен в чорний список."""
    _token_blacklist.add(jti)


def is_token_blacklisted(jti: str) -> bool:
    """Перевірка, чи токен в чорному списку."""
    return jti in _token_blacklist


def clear_blacklist() -> None:
    """Очистити чорний список (для тестування)."""
    _token_blacklist.clear()


def get_blacklist_size() -> int:
    """Отримати розмір чорного списку."""
    return len(_token_blacklist)


# ============================================================
# ЕКСПОРТ
# ============================================================

__all__ = [
    # Основні функції
    "hash_password",
    "get_password_hash",      # ← Аліас для сумісності!
    "verify_password",
    
    # Пароль
    "is_password_strong",
    "generate_secure_password",
    
    # Токени
    "create_access_token",
    "create_refresh_token",
    "refresh_access_token",
    
    # Декодування/верифікація
    "decode_token",
    "verify_token",
    "get_token_payload",
    "get_token_expiration",
    "is_token_expired",
    "get_token_type",
    "get_token_jti",
    "get_user_id_from_token",
    "get_username_from_token",
    
    # Валідація
    "validate_token_type",
    "validate_token_user",
    
    # Блек-лист
    "add_to_blacklist",
    "is_token_blacklisted",
    "clear_blacklist",
    "get_blacklist_size",
]