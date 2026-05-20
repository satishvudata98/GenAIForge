from collections.abc import Sequence
from uuid import uuid4

from qdrant_client import AsyncQdrantClient, models

from app.config import get_settings
from app.core.tracing import observe

settings = get_settings()


def build_point(
    *,
    vector: Sequence[float],
    payload: dict[str, object],
    point_id: str | None = None,
) -> models.PointStruct:
    return models.PointStruct(
        id=point_id or uuid4().hex,
        vector=list(vector),
        payload=payload,
    )


class QdrantStore:
    def __init__(self, url: str | None = None) -> None:
        self._client = AsyncQdrantClient(
            url=url or str(settings.qdrant_url),
            check_compatibility=False,
        )

    @observe(name="qdrant_create_collection")
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int | None = None,
    ) -> None:
        exists = await self._client.collection_exists(collection_name)
        if exists:
            return

        await self._client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size or settings.embedding_dimensions,
                distance=models.Distance.COSINE,
            ),
            hnsw_config=models.HnswConfigDiff(m=16, ef_construct=100),
        )

    @observe(name="qdrant_upsert")
    async def upsert(
        self,
        collection_name: str,
        points: Sequence[models.PointStruct],
    ) -> None:
        if not points:
            return

        await self._client.upsert(
            collection_name=collection_name,
            wait=True,
            points=list(points),
        )

    @observe(name="qdrant_search")
    async def search(
        self,
        collection_name: str,
        query_vector: Sequence[float],
        top_k: int = 5,
        query_filter: models.Filter | None = None,
    ) -> list[models.ScoredPoint]:
        response = await self._client.query_points(
            collection_name=collection_name,
            query=list(query_vector),
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )
        return response.points

    async def close(self) -> None:
        await self._client.close()
