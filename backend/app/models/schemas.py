from decimal import Decimal
from typing import Any, Generic, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class TokenUsage(BaseModel):
    input: int | None = None
    output: int | None = None


class ResponseMeta(BaseModel):
    request_id: str
    model: str | None = None
    latency_ms: int | None = None
    tokens: TokenUsage | None = None
    cost_usd: Decimal | None = None
    cache: Literal["HIT", "MISS"] | None = None


class ApiResponse(BaseModel, Generic[DataT]):
    data: DataT
    meta: ResponseMeta


class ErrorResponseDetail(BaseModel):
    code: str
    message: str
    request_id: str
    retry_after: int | None = None


class ErrorResponse(BaseModel):
    error: ErrorResponseDetail


class SseEvent(BaseModel):
    type: Literal["chunk", "source", "meta", "done"]
    content: Any | None = None
    index: int | None = None


class IngestRequest(BaseModel):
    collection_name: str = Field(min_length=1)
    chunk_size: int = Field(default=512, ge=64, le=4096)
    chunk_overlap: int = Field(default=64, ge=0, le=1024)


class IngestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    collection_id: UUID
    collection_name: str
    qdrant_collection_name: str
    documents_ingested: int
    chunks_indexed: int
    embedding_model: str
    estimated_cost_usd: Decimal | None = None


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    collection_id: UUID
    model: str = "gpt-4o-mini"
    top_k: int = Field(default=5, ge=1, le=20)
    use_reranker: bool = True
