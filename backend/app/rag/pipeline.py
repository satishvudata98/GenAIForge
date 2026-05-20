import json
from collections.abc import AsyncGenerator, Sequence
from time import perf_counter

from app.core.llm_clients import stream_completion
from app.core.tracing import observe
from app.models.schemas import SseEvent
from app.rag.retrieval import RetrievedChunk


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
    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise assistant. Answer using only the provided context. "
                "Cite each claim with the source number in brackets, e.g. [1]. "
                "If the context is insufficient, say so explicitly."
            ),
        },
        {
            "role": "user",
            "content": f"Question: {query}\n\nContext:\n{context}",
        },
    ]

    token_gen = await stream_completion(model=model, messages=messages)

    async def _gen() -> AsyncGenerator[str, None]:
        chunk_index = 0
        try:
            async for delta in token_gen:
                yield format_sse_event(SseEvent(type="chunk", content=delta, index=chunk_index))
                chunk_index += 1
        except Exception as exc:
            yield format_sse_event(SseEvent(type="chunk", content=f"\n\n[Error: {exc}]", index=chunk_index))
            yield format_sse_event(SseEvent(type="done"))
            return

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

    return _gen()
