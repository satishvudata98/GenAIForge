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
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    postgres_dsn: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/genai_forge"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: AnyHttpUrl = "http://localhost:6333"
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072

    openai_api_key: str | None = None
    cohere_api_key: str | None = None
    langfuse_host: AnyHttpUrl | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_disabled: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
