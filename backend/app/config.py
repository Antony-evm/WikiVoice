from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    database_url: str
    test_database_url: str | None = None
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_recycle: int = 3600
    database_pool_timeout: int = 30
    request_timeout: float = 20.0

    stytch_secret: str
    stytch_project_id: str
    stytch_public_token: str | None = None

    environment: str
    debug: bool
    json_logs: bool = False
    log_level: str = "INFO"

    port: int = 8000
    workers: int = 1
    max_requests_per_worker: int = 10000
    max_requests_jitter: int = 1000
    shutdown_timeout_seconds: int = 30

    openai_api_key: str
    frontend_url: str = "http://localhost:5173"  # Vite dev server default

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings instance."""
    return Settings()
