from datetime import datetime, timedelta
from jose import jwt

# Якщо у settings є SECRET_KEY — використовуємо його
try:
    from app.core.settings import settings
    SECRET_KEY = settings.SECRET_KEY
except Exception:
    SECRET_KEY = "CHANGE_ME_SUPER_SECRET_KEY"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Створює JWT токен з payload (data) та часом життя.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
