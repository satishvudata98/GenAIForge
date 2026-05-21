from collections.abc import Callable
from functools import lru_cache
from typing import Any, TypeVar

from langfuse import Langfuse
from langfuse.decorators import langfuse_context
from langfuse.decorators import observe as langfuse_observe

from app.config import get_settings

settings = get_settings()

WrappedCallable = TypeVar("WrappedCallable", bound=Callable[..., Any])

# Pricing table: model → (input $/1M tokens, output $/1M tokens)
_MODEL_PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "llama-3.3-70b-versatile": (0.59, 0.79),
    "openai/gpt-oss-120b": (0.90, 0.90),
    "gemini-2.5-flash": (0.15, 0.60),
    "gemini-3.1-flash-lite": (0.075, 0.30),
    "text-embedding-3-large": (0.13, 0.0),
    "rerank-english-v3.0": (2.00, 0.0),
}


def count_tokens_approx(text: str) -> int:
    """Approximate token count at ~4 chars per token."""
    return max(1, len(text) // 4)


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int = 0) -> float:
    """Estimate API cost in USD from token counts."""
    in_price, out_price = _MODEL_PRICING.get(model, (2.50, 10.00))
    return round((input_tokens / 1_000_000) * in_price + (output_tokens / 1_000_000) * out_price, 8)


def update_span_usage(model: str, input_text: str, output_text: str = "") -> None:
    """Update LangFuse span + Prometheus counters with token usage and estimated cost.

    Safe to call outside @observe() — silently skips if no active span.
    """
    from app.observability.metrics import LLM_ESTIMATED_COST_USD, LLM_TOKENS_TOTAL

    input_tokens = count_tokens_approx(input_text)
    output_tokens = count_tokens_approx(output_text)
    cost = estimate_cost_usd(model, input_tokens, output_tokens)

    LLM_TOKENS_TOTAL.labels(model=model, token_type="prompt").inc(input_tokens)
    if output_tokens:
        LLM_TOKENS_TOTAL.labels(model=model, token_type="completion").inc(output_tokens)
    LLM_ESTIMATED_COST_USD.labels(model=model).inc(cost)

    if settings.langfuse_disabled:
        return
    try:
        langfuse_context.update_current_observation(
            model=model,
            usage={"input": input_tokens, "output": output_tokens, "unit": "TOKENS"},
            metadata={"estimated_cost_usd": cost},
        )
    except Exception:
        pass


@lru_cache
def get_langfuse_client() -> Langfuse | None:
    if settings.langfuse_disabled:
        return None
    if not all(
        [
            settings.langfuse_host,
            settings.langfuse_public_key,
            settings.langfuse_secret_key,
        ]
    ):
        return None

    return Langfuse(
        host=str(settings.langfuse_host),
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
    )


def observe(*args: Any, **kwargs: Any):
    if settings.langfuse_disabled:
        if args and callable(args[0]) and len(args) == 1 and not kwargs:
            return args[0]

        def passthrough(func: WrappedCallable) -> WrappedCallable:
            return func

        return passthrough

    return langfuse_observe(*args, **kwargs)
