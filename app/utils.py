from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional

# === Конфігурація JWT ===
SECRET_KEY = "supersecretkey"  # ⚠️ винеси у .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# === Налаштування для хешування паролів ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# === Хешування пароля ===
def get_password_hash(password: str) -> str:
    # bcrypt підтримує максимум 72 байти
    if len(password.encode("utf-8")) > 72:
        password = password[:72]
    return pwd_context.hash(password)


# === Перевірка пароля ===
def verify_password(plain_password: str, hashed_password: str) -> bool:
    if len(plain_password.encode("utf-8")) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


# === Створення JWT токена ===
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# === Перевірка та декодування JWT токена ===
def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
