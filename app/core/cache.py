"""
Простий кеш для аналітичних даних
"""
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

class SimpleCache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
    
    def get(self, key: str, ttl: int = 30) -> Optional[Any]:
        """Отримати з кешу"""
        if key in self._cache and key in self._timestamps:
            if datetime.utcnow() - self._timestamps[key] < timedelta(seconds=ttl):
                return self._cache[key]
            else:
                # Видаляємо прострочені
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Зберегти в кеш"""
        self._cache[key] = value
        self._timestamps[key] = datetime.utcnow()
    
    def clear(self) -> None:
        """Очистити кеш"""
        self._cache.clear()
        self._timestamps.clear()

# Глобальний екземпляр кешу
cache = SimpleCache()