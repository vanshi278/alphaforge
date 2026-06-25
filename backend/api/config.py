"""Application configuration, loaded from environment variables (.env supported).

Keeping this dependency-light (python-dotenv + os.environ) avoids pinning a
settings library this early. Swap for pydantic-settings later if it earns its keep.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # read a local .env if present; real env vars take precedence


def _env(key: str, default: str) -> str:
    return os.getenv(key, default)


@dataclass(frozen=True)
class Settings:
    app_env: str = _env("APP_ENV", "dev")
    log_level: str = _env("LOG_LEVEL", "INFO")

    # Postgres / TimescaleDB
    pg_host: str = _env("POSTGRES_HOST", "localhost")
    pg_port: int = int(_env("POSTGRES_PORT", "5432"))
    pg_user: str = _env("POSTGRES_USER", "alphaforge")
    pg_password: str = _env("POSTGRES_PASSWORD", "alphaforge")
    pg_db: str = _env("POSTGRES_DB", "alphaforge")

    # Redis
    redis_url: str = _env("REDIS_URL", "redis://localhost:6379/0")

    @property
    def pg_dsn(self) -> str:
        return (
            f"host={self.pg_host} port={self.pg_port} "
            f"dbname={self.pg_db} user={self.pg_user} password={self.pg_password}"
        )


settings = Settings()
