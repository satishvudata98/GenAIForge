from dataclasses import dataclass
from typing import Any

from cohere import AsyncClient

from app.config import get_settings
from app.core.embeddings import embed_texts
from app.core.tracing import observe
from app.core.vector_store import QdrantStore

settings = get_settings()


@dataclass(slots=True)
class RetrievedChunk:
    text: str
    score: float
    document_id: str | None
    source_file: str | None
    page_number: int | str | None

    def to_source_payload(self) -> dict[str, Any]:
        return {
            "chunk": self.text,
            "score": self.score,
            "doc": self.source_file,
            "page": self.page_number,
            "document_id": self.document_id,
        }


def _get_cohere_client() -> AsyncClient:
    if not settings.cohere_api_key:
        raise RuntimeError("COHERE_API_KEY is required when reranking is enabled.")
    return AsyncClient(api_key=settings.cohere_api_key)


@observe(name="qdrant_vector_search")
async def _qdrant_search(
    store: QdrantStore, collection_name: str, query_vector: list[float], top_k: int
) -> list:
    return await store.search(collection_name=collection_name, query_vector=query_vector, top_k=top_k)


@observe(name="cohere_rerank")
async def _cohere_rerank(
    query: str, chunks: "list[RetrievedChunk]", top_k: int
) -> "list[RetrievedChunk]":
    rerank_response = await _get_cohere_client().rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=[chunk.text for chunk in chunks],
        top_n=top_k,
    )
    return [
        RetrievedChunk(
            text=chunks[r.index].text,
            score=float(r.relevance_score),
            document_id=chunks[r.index].document_id,
            source_file=chunks[r.index].source_file,
            page_number=chunks[r.index].page_number,
        )
        for r in rerank_response.results
    ]


@observe(name="rag_retrieve")
async def retrieve_chunks(
    *,
    query: str,
    collection_name: str,
    top_k: int,
    use_reranker: bool,
    vector_store: QdrantStore | None = None,
) -> list[RetrievedChunk]:
    if not query.strip():
        raise ValueError("Query text must not be empty.")

    store = vector_store or QdrantStore()
    try:
        query_vector = (await embed_texts([query]))[0]
        raw_hits = await _qdrant_search(
            store, collection_name, query_vector, top_k * 3 if use_reranker else top_k
        )
    finally:
        if vector_store is None:
            await store.close()

    chunks = [
        RetrievedChunk(
            text=str((hit.payload or {}).get("text", "")),
            score=float(hit.score),
            document_id=(hit.payload or {}).get("document_id"),
            source_file=(hit.payload or {}).get("source_file"),
            page_number=(hit.payload or {}).get("page_number"),
        )
        for hit in raw_hits
        if (hit.payload or {}).get("text")
    ]

    if not use_reranker or not chunks:
        return chunks[:top_k]

    return await _cohere_rerank(query, chunks, top_k)
