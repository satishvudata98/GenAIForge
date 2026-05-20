from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_name: str = "GenAI Forge API"
    environment: Literal["local", "development", "test", "staging", "production"] = "local"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    api_v1_prefix: str = "/v1"
    allowed_origins: list[str] = [
        "http://localhost:43010",
        "http://127.0.0.1:43010",
        "http://localhost:48080",
        "http://127.0.0.1:48080",
    ]

    postgres_dsn: str = "postgresql+asyncpg://postgres:postgres@localhost:55432/genai_forge"
    redis_url: str = "redis://localhost:56379/0"
    qdrant_url: AnyHttpUrl = "http://localhost:56333"
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072

    openai_api_key: str | None = None
    cohere_api_key: str | None = None
    groq_api_key: str | None = None
    google_api_key: str | None = None
    xai_api_key: str | None = None
    tavily_api_key: str | None = None

    langfuse_host: AnyHttpUrl | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_disabled: bool = False

    # Day 8: semantic cache & rate limiting
    semantic_cache_threshold: float = 0.95
    semantic_cache_ttl: int = 3600
    semantic_cache_max_entries: int = 500
    rate_limit_rpm: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
