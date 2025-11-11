from __future__ import annotations

import os
from pydantic import BaseSettings, AnyUrl, Field, validator


class Settings(BaseSettings):
    # Core
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Secrets and external services
    DATABASE_URL: str = Field(default="postgresql+psycopg2://postgres:postgres@db:5432/agentic")
    REDIS_URL: str = Field(default="redis://redis:6379/0")

    OPENAI_API_KEY: str | None = Field(default=None)
    CREW_API_BASE: AnyUrl | None = Field(default=None)
    CREW_API_KEY: str | None = Field(default=None)
    CREW_WEBHOOK_SECRET: str = Field(default="changeme-webhook-secret")

    # Auth
    JWT_SECRET: str = Field(default="changeme-jwt-secret")
    JWT_ALG: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=60 * 8)

    @validator("DATABASE_URL")
    def _ensure_db_url(cls, v: str) -> str:  # noqa: N805
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v


settings = Settings(_env_file=os.getenv("ENV_FILE", ".env"), _env_file_encoding="utf-8")


