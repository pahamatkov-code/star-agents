# -*- coding: utf-8 -*-
"""
Конфігурація додатку Star Agents — ПРОФЕСІЙНА ФІНАЛЬНА ВЕРСІЯ 3.0.0
"""
import os
import warnings
from pathlib import Path
from typing import List, Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ValidationError
from dotenv import load_dotenv

# Завантажуємо .env файл
load_dotenv()


class Settings(BaseSettings):
    """
    Головні налаштування додатку.
    Всі змінні завантажуються з .env або використовують значення за замовчуванням.
    """

    # ============================================================
    # БАЗОВІ НАЛАШТУВАННЯ
    # ============================================================
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    PROJECT_NAME: str = "Star Agents"
    VERSION: str = "3.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes", "on")
    ENVIRONMENT: Literal["development", "staging", "production"] = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # ✅ ДОДАНО

    # ============================================================
    # БАЗА ДАНИХ
    # ============================================================
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "star_agents")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() in ("true", "1", "yes", "on")

    # ============================================================
    # БЕЗПЕКА ТА JWT
    # ============================================================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # ============================================================
    # CORS
    # ============================================================
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000"
    ).split(",")

    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = ["Authorization", "Content-Type", "Accept", "X-Requested-With"]
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "True").lower() in ("true", "1", "yes", "on")

    # ============================================================
    # RATE LIMITING
    # ============================================================
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() in ("true", "1", "yes", "on")
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    RATE_LIMIT_PER_DAY: int = int(os.getenv("RATE_LIMIT_PER_DAY", "10000"))

    # ============================================================
    # КЕШУВАННЯ
    # ============================================================
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() in ("true", "1", "yes", "on")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "30"))
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "100"))

    # ============================================================
    # МЕТРИКИ
    # ============================================================
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() in ("true", "1", "yes", "on")
    ENABLE_LOGGING: bool = os.getenv("ENABLE_LOGGING", "True").lower() in ("true", "1", "yes", "on")
    ENABLE_HSTS: bool = os.getenv("ENABLE_HSTS", "True").lower() in ("true", "1", "yes", "on")

    # ============================================================
    # ТЕЛЕГРАМ БОТ
    # ============================================================
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "http://localhost:8000/chat/webhook")

    # ============================================================
    # OPENROUTER (AI/LLM)
    # ============================================================
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    # ============================================================
    # N8N АВТОМАТИЗАЦІЯ
    # ============================================================
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook")
    N8N_API_KEY: Optional[str] = os.getenv("N8N_API_KEY")

    # ============================================================
    # АДМІНІСТРАТОР
    # ============================================================
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")

    # ============================================================
    # АНАЛІТИКА
    # ============================================================
    ANALYTICS_MAX_TOP_ITEMS: int = int(os.getenv("ANALYTICS_MAX_TOP_ITEMS", "10"))
    ANALYTICS_TIMELINE_HOURS: int = int(os.getenv("ANALYTICS_TIMELINE_HOURS", "24"))
    ANALYTICS_RECENT_MESSAGES: int = int(os.getenv("ANALYTICS_RECENT_MESSAGES", "20"))

    # ============================================================
    # ВАЛІДАЦІЯ
    # ============================================================
    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if v == "CHANGE_ME_IN_PRODUCTION":
            warnings.warn("⚠️ SECRET_KEY не змінено! Це небезпечно для продакшну!", UserWarning)
        return v

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        if not v or "sqlite" in v.lower():
            raise ValueError("❌ DATABASE_URL має бути PostgreSQL, а не SQLite!")
        return v

    @field_validator("TELEGRAM_BOT_TOKEN")
    def validate_telegram_token(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith(":"):
            # Дозволяємо пусті значення
            pass
        return v

    # ============================================================
    # ДОДАТКОВІ МЕТОДИ
    # ============================================================
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    def is_staging(self) -> bool:
        return self.ENVIRONMENT == "staging"

    def get_database_url(self) -> str:
        return self.DATABASE_URL

    def get_telegram_token(self) -> Optional[str]:
        return self.TELEGRAM_BOT_TOKEN

    def get_openrouter_key(self) -> Optional[str]:
        return self.OPENROUTER_API_KEY


# ============================================================
# ІНІЦІАЛІЗАЦІЯ
# ============================================================
try:
    settings = Settings()
    print("✅ Settings loaded successfully!")
    print(f"🔧 Environment: {settings.ENVIRONMENT}")
    print(f"🐛 Debug: {settings.DEBUG}")
    print(f"📊 Log Level: {settings.LOG_LEVEL}")
    print(f"🗄️  Database: {settings.DATABASE_URL}")
    if settings.TELEGRAM_BOT_TOKEN:
        print("🤖 Telegram: configured")
    if settings.OPENROUTER_API_KEY:
        print("🧠 OpenRouter: configured")
except ValidationError as e:
    print("❌ Settings validation error:")
    print(e)
    raise


__all__ = ["settings", "Settings"]