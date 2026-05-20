"""Unified LLM client — routes to the correct provider via OpenAI-compatible endpoints.

All four providers expose an OpenAI-compatible chat-completions API, so a single
AsyncOpenAI client instance with the appropriate base_url covers all of them.
No additional SDKs required.
"""
from collections.abc import AsyncGenerator
from typing import Literal

from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, InternalServerError, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.core.tracing import observe

settings = get_settings()

Provider = Literal["openai", "groq", "gemini"]

_PROVIDER_CONFIGS: dict[str, dict] = {
    "openai": {
        "base_url": None,
        "key_attr": "openai_api_key",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_attr": "groq_api_key",
    },
    "gemini": {
        # Google AI Studio OpenAI-compatible endpoint (GA since late 2024)
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_attr": "google_api_key",
    },
}

# Model → provider routing table
SUPPORTED_MODELS: dict[str, Provider] = {
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "openai/gpt-oss-120b": "groq",
    "llama-3.3-70b-versatile": "groq",
    "gemini-3.1-flash-lite": "gemini",
    "gemini-2.5-flash": "gemini",
}


def infer_provider(model: str) -> Provider:
    return SUPPORTED_MODELS.get(model, "openai")


# Module-level cache so clients are not GC'd while their streams are still open.
_CLIENT_CACHE: dict[Provider, AsyncOpenAI] = {}


def build_client(provider: Provider) -> AsyncOpenAI:
    if provider in _CLIENT_CACHE:
        return _CLIENT_CACHE[provider]
    cfg = _PROVIDER_CONFIGS[provider]
    api_key: str | None = getattr(settings, cfg["key_attr"], None)
    if not api_key:
        raise RuntimeError(
            f"API key for provider '{provider}' is not configured. "
            f"Set the '{cfg['key_attr'].upper()}' environment variable."
        )
    kwargs: dict = {"api_key": api_key}
    if cfg["base_url"]:
        kwargs["base_url"] = cfg["base_url"]
    client = AsyncOpenAI(**kwargs)
    _CLIENT_CACHE[provider] = client
    return client


@retry(
    retry=retry_if_exception_type((APIConnectionError, APITimeoutError, InternalServerError, RateLimitError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
@observe(name="llm_stream_completion")
async def stream_completion(
    *,
    model: str,
    messages: list[dict],
) -> AsyncGenerator[str, None]:
    """Yield text delta tokens from any supported provider's chat-completion API."""
    provider = infer_provider(model)
    client = build_client(provider)
    stream = await client.chat.completions.create(model=model, messages=messages, stream=True)

    async def _gen() -> AsyncGenerator[str, None]:
        async for event in stream:
            delta = event.choices[0].delta.content if event.choices else None
            if delta:
                yield delta

    return _gen()
