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

    # -----------------------------
    # Database
    # -----------------------------
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite:///./agents.db"),
        description="Основний URL бази даних"
    )

    # -----------------------------
    # Security / JWT
    # -----------------------------
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION"),
        description="Секретний ключ для JWT"
    )
    ALGORITHM: str = Field(default=os.getenv("ALGORITHM", "HS256"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    )

    # -----------------------------
    # Admin (seed)
    # -----------------------------
    admin_user: str = Field(default="admin@example.com")
    admin_pass: str = Field(default="admin123")

    # -----------------------------
    # LLM / OpenRouter
    # -----------------------------
    OPENROUTER_API_KEY: str | None = Field(
        default=os.getenv("OPENROUTER_API_KEY")
    )
    OPENROUTER_MODEL: str | None = Field(
        default=os.getenv("OPENROUTER_MODEL")
    )

    # -----------------------------
    # Optional API keys
    # -----------------------------
    anthropic_api_key: str | None = Field(default=os.getenv("ANTHROPIC_API_KEY"))
    openai_api_key: str | None = Field(default=os.getenv("OPENAI_API_KEY"))

    # -----------------------------
    # PostgreSQL (на майбутнє)
    # -----------------------------
    postgres_user: str | None = Field(default=os.getenv("POSTGRES_USER"))
    postgres_password: str | None = Field(default=os.getenv("POSTGRES_PASSWORD"))
    postgres_db: str | None = Field(default=os.getenv("POSTGRES_DB"))

    # -----------------------------
    # Debug
    # -----------------------------
    DEBUG: bool = Field(default=bool(os.getenv("DEBUG", False)))

    # -----------------------------
    # Pydantic v2 config
    # -----------------------------
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
