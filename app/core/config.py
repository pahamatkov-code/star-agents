import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic import ConfigDict


class Settings(BaseSettings):
    # -----------------------------
    # Base paths
    # -----------------------------
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DB_FILE: Path = BASE_DIR / "agents.db"

    # -----------------------------
    # Database
    # -----------------------------
    DATABASE_URL: str = Field(
        default_factory=lambda: f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'agents.db'}",
        description="Основний URL бази даних"
    )

    # -----------------------------
    # Security / JWT
    # -----------------------------
    SECRET_KEY: str = Field(
        default="CHANGE_ME_IN_PRODUCTION",
        description="Секретний ключ для JWT"
    )
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440   # 24 години
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7        # 7 днів

    # -----------------------------
    # Admin (seed)
    # -----------------------------
    admin_user: str = "admin@example.com"
    admin_pass: str = "admin123"

    # -----------------------------
    # Optional API keys
    # -----------------------------
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    # -----------------------------
    # PostgreSQL (на майбутнє)
    # -----------------------------
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_db: str | None = None

    # -----------------------------
    # Debug
    # -----------------------------
    DEBUG: bool = False

    # -----------------------------
    # Pydantic v2 config
    # -----------------------------
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
