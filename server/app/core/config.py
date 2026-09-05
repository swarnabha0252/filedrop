import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/filedrop"
    DATABASE_URL_UNPOOLED: str | None = None
    MAX_FILE_SIZE_MB: int = 100
    FRONTEND_URL: str = "http://localhost:5173"
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "./storage"
    ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    TOKEN_LENGTH: int = 24
    CLEANUP_INTERVAL_SECONDS: int = 3600
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def database_url_pooled(self) -> str:
        """Return the pooled connection URL for application runtime.
        Prefers Vercel Neon's DATABASE_DATABASE_URL, falls back to DATABASE_URL.
        """
        return os.getenv("DATABASE_DATABASE_URL") or self.DATABASE_URL

    @property
    def database_url_unpooled(self) -> str:
        """Return the unpooled/direct connection URL for migrations.
        Prefers Vercel Neon's DATABASE_DATABASE_URL_UNPOOLED, falls back to DATABASE_URL_UNPOOLED,
        then to DATABASE_URL.
        """
        return (
            os.getenv("DATABASE_DATABASE_URL_UNPOOLED")
            or os.getenv("DATABASE_POSTGRES_URL_NON_POOLING")
            or self.DATABASE_URL_UNPOOLED
            or self.database_url_pooled
        )


settings = Settings()