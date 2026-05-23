import asyncio
import json
import math
from collections.abc import AsyncGenerator
from time import perf_counter
from typing import Any

from redis.asyncio import Redis

from app.config import get_settings
from app.core.embeddings import embed_texts
from app.models.schemas import SseEvent

settings = get_settings()

_CACHE_KEY = "semantic_cache:v1:entries"


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


def _get_redis() -> Redis:
    return Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)


async def get_cached_response(query: str) -> dict[str, Any] | None:
    """Return a cached entry if a semantically similar query exists above the threshold.

    Returns None gracefully when Redis or the embedding service is unavailable.
    """
    try:
        query_vec = (await embed_texts([query]))[0]
        async with _get_redis() as redis:
            raw_entries = await redis.lrange(_CACHE_KEY, 0, -1)
    except Exception:
        return None
    for raw in raw_entries:
        entry = json.loads(raw)
        if _cosine(query_vec, entry["embedding"]) >= settings.semantic_cache_threshold:
            return entry
    return None


async def store_cached_response(
    query: str,
    response_text: str,
    sources: list[dict[str, Any]],
) -> None:
    """Embed the query and persist the response for future hits."""
    query_vec = (await embed_texts([query]))[0]
    entry = json.dumps({"embedding": query_vec, "response_text": response_text, "sources": sources})
    async with _get_redis() as redis:
        pipe = redis.pipeline()
        pipe.rpush(_CACHE_KEY, entry)
        pipe.ltrim(_CACHE_KEY, -settings.semantic_cache_max_entries, -1)
        pipe.expire(_CACHE_KEY, settings.semantic_cache_ttl)
        await pipe.execute()


def replay_cached_sse(
    entry: dict[str, Any],
    *,
    request_id: str,
    started_at: float,
    model: str,
) -> AsyncGenerator[str, None]:
    """Replay a cache-hit entry as an SSE stream, word-level to preserve streaming UX."""

    async def _gen() -> AsyncGenerator[str, None]:
        text: str = entry["response_text"]
        sources: list[dict] = entry["sources"]

        words = text.split()
        for i, word in enumerate(words):
            content = word if i == len(words) - 1 else word + " "
            chunk_event = SseEvent(type="chunk", content=content, index=i)
            yield f"data: {json.dumps(chunk_event.model_dump(mode='json'))}\n\n"

        for src in sources:
            src_event = SseEvent(type="source", content=src)
            yield f"data: {json.dumps(src_event.model_dump(mode='json'))}\n\n"

        latency_ms = int((perf_counter() - started_at) * 1000)
        meta_content = {
            "request_id": request_id,
            "model": model,
            "latency_ms": latency_ms,
            "sources": len(sources),
            "cache": "HIT",
        }
        meta_event = SseEvent(type="meta", content=meta_content)
        yield f"data: {json.dumps(meta_event.model_dump(mode='json'))}\n\n"
        yield f"data: {json.dumps(SseEvent(type='done').model_dump(mode='json'))}\n\n"

    return _gen()


async def capturing_sse_stream(
    gen: AsyncGenerator[str, None],
    *,
    query: str,
) -> AsyncGenerator[str, None]:
    """Wrap an SSE generator, pass events through, then fire-and-forget cache store."""

    async def _gen() -> AsyncGenerator[str, None]:
        text_parts: list[str] = []
        sources: list[dict] = []

        async for event_str in gen:
            yield event_str
            if not event_str.startswith("data: "):
                continue
            try:
                payload = json.loads(event_str[6:].strip())
                if payload.get("type") == "chunk":
                    text_parts.append(payload.get("content", ""))
                elif payload.get("type") == "source":
                    sources.append(payload.get("content", {}))
            except (json.JSONDecodeError, KeyError):
                pass

        response_text = "".join(text_parts)
        if response_text:
            asyncio.create_task(store_cached_response(query, response_text, sources))

    return _gen()
