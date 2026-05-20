from collections.abc import Sequence
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.embeddings import embed_texts
from app.core.tracing import observe
from app.core.vector_store import QdrantStore, build_point
from app.models.db import RagCollection
from app.models.schemas import IngestResponse

settings = get_settings()


def _normalize_collection_name(collection_name: str) -> str:
    return "-".join(collection_name.strip().lower().split())


def _build_qdrant_collection_name(collection_name: str) -> str:
    return f"{_normalize_collection_name(collection_name)}-{uuid4().hex[:8]}"


def _estimate_embedding_cost_usd(chunk_texts: Sequence[str]) -> Decimal:
    estimated_tokens = sum(max(1, len(text) // 4) for text in chunk_texts)
    # Approximate text-embedding-3-large pricing: $0.00013 / 1K tokens.
    return (Decimal(estimated_tokens) / Decimal(1000)) * Decimal("0.00013")


@observe(name="rag_ingest")
async def ingest_documents(
    *,
    file_paths: Sequence[Path],
    collection_name: str,
    chunk_size: int,
    chunk_overlap: int,
    db: AsyncSession,
    vector_store: QdrantStore | None = None,
) -> IngestResponse:
    from llama_index.core import SimpleDirectoryReader
    from llama_index.core.node_parser import SentenceSplitter

    if not file_paths:
        raise ValueError("At least one file must be provided for ingestion.")

    reader = SimpleDirectoryReader(input_files=[str(path) for path in file_paths])
    documents = reader.load_data()
    if not documents:
        raise ValueError("No readable documents were found in the uploaded files.")

    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nodes = splitter.get_nodes_from_documents(documents)

    unique_chunks: list[tuple[str, str, object]] = []
    seen_hashes: set[str] = set()
    for node in nodes:
        text = node.get_content().strip()
        if not text:
            continue
        chunk_hash = sha256(text.encode("utf-8")).hexdigest()
        if chunk_hash in seen_hashes:
            continue
        seen_hashes.add(chunk_hash)
        unique_chunks.append((chunk_hash, text, node))

    if not unique_chunks:
        raise ValueError("No text chunks were produced from the uploaded files.")

    result = await db.execute(select(RagCollection).where(RagCollection.name == collection_name))
    collection = result.scalars().first()
    if collection is None:
        collection = RagCollection(
            name=collection_name,
            qdrant_collection_name=_build_qdrant_collection_name(collection_name),
            doc_count=0,
            chunk_count=0,
            embedding_model=settings.embedding_model,
        )
        db.add(collection)
        await db.flush()

    store = vector_store or QdrantStore()
    try:
        await store.create_collection(collection.qdrant_collection_name)
        texts = [text for _, text, _ in unique_chunks]
        vectors = await embed_texts(texts)

        points = []
        for (chunk_hash, text, node), vector in zip(unique_chunks, vectors, strict=True):
            metadata = getattr(node, "metadata", {}) or {}
            page_number = metadata.get("page_number") or metadata.get("page_label")
            source_file = metadata.get("file_name") or Path(
                str(metadata.get("file_path") or "unknown")
            ).name
            point_id = sha256(f"{collection.id}:{chunk_hash}".encode("utf-8")).hexdigest()
            payload = {
                "document_id": str(getattr(node, "ref_doc_id", None) or getattr(node, "node_id", point_id)),
                "collection_id": str(collection.id),
                "text": text,
                "page_number": page_number,
                "source_file": source_file,
            }
            points.append(build_point(vector=vector, payload=payload, point_id=point_id))

        await store.upsert(collection.qdrant_collection_name, points)
    finally:
        if vector_store is None:
            await store.close()

    collection.doc_count += len(documents)
    collection.chunk_count += len(unique_chunks)
    collection.embedding_model = settings.embedding_model

    await db.commit()
    await db.refresh(collection)

    return IngestResponse(
        collection_id=collection.id,
        collection_name=collection.name,
        qdrant_collection_name=collection.qdrant_collection_name,
        documents_ingested=len(documents),
        chunks_indexed=len(unique_chunks),
        embedding_model=collection.embedding_model,
        estimated_cost_usd=_estimate_embedding_cost_usd(texts),
    )
