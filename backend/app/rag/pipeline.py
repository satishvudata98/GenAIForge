import json
from collections.abc import AsyncGenerator, Sequence
from time import perf_counter

from openai import AsyncOpenAI

from app.config import get_settings
from app.core.tracing import observe
from app.models.schemas import SseEvent
from app.rag.retrieval import RetrievedChunk

settings = get_settings()


def _get_openai_client() -> AsyncOpenAI:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required to generate answers.")
    return AsyncOpenAI(api_key=settings.openai_api_key)


def format_sse_event(event: SseEvent) -> str:
    return f"data: {json.dumps(event.model_dump(mode='json'))}\n\n"


def _build_context(chunks: Sequence[RetrievedChunk]) -> str:
    sections = []
    for index, chunk in enumerate(chunks, start=1):
        sections.append(
            f"[{index}] Source: {chunk.source_file or 'unknown'} | Page: {chunk.page_number or 'n/a'}\n{chunk.text}"
        )
    return "\n\n".join(sections)


@observe(name="rag_stream")
async def stream_rag_response(
    *,
    query: str,
    chunks: Sequence[RetrievedChunk],
    model: str,
    request_id: str,
    started_at: float,
) -> AsyncGenerator[str, None]:
    context = _build_context(chunks)
    client = _get_openai_client()

    stream = await client.chat.completions.create(
        model=model,
        stream=True,
        messages=[
            {
                "role": "system",
                "content": "Answer the user using only the provided context. Cite uncertainty when context is insufficient.",
            },
            {
                "role": "user",
                "content": f"Question: {query}\n\nContext:\n{context}",
            },
        ],
    )

    chunk_index = 0
    async for event in stream:
        delta = event.choices[0].delta.content if event.choices else None
        if not delta:
            continue

        yield format_sse_event(SseEvent(type="chunk", content=delta, index=chunk_index))
        chunk_index += 1

    for chunk in chunks:
        yield format_sse_event(SseEvent(type="source", content=chunk.to_source_payload()))

    latency_ms = int((perf_counter() - started_at) * 1000)
    yield format_sse_event(
        SseEvent(
            type="meta",
            content={
                "request_id": request_id,
                "model": model,
                "latency_ms": latency_ms,
                "sources": len(chunks),
            },
        )
    )
    yield format_sse_event(SseEvent(type="done"))
