from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.semantic_cache import capturing_sse_stream, get_cached_response, replay_cached_sse
from app.dependencies import get_db
from app.middleware import check_rate_limit
from app.observability.metrics import RAG_CACHE_HITS, RAG_CACHE_MISSES
from app.models.db import RagCollection
from app.models.schemas import (
    ApiResponse,
    ErrorResponse,
    ErrorResponseDetail,
    IngestResponse,
    QueryRequest,
    ResponseMeta,
)
from app.rag.ingestion import ingest_documents
from app.rag.pipeline import stream_rag_response
from app.rag.retrieval import retrieve_chunks

router = APIRouter(prefix="/rag", tags=["rag"])

_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def build_meta(request: Request) -> ResponseMeta:
    return ResponseMeta(request_id=getattr(request.state, "request_id", "unknown"))


def error_response(
    *,
    code: str,
    message: str,
    request: Request,
    status_code: int,
) -> JSONResponse:
    payload = ErrorResponse(
        error=ErrorResponseDetail(
            code=code,
            message=message,
            request_id=getattr(request.state, "request_id", "unknown"),
        )
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


@router.get("/collections")
async def list_collections_route(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RagCollection).order_by(RagCollection.created_at.desc()))
    collections = result.scalars().all()
    data = [
        {
            "id": str(c.id),
            "name": c.name,
            "chunk_count": c.chunk_count,
            "doc_count": c.doc_count,
            "created_at": c.created_at.isoformat(),
        }
        for c in collections
    ]
    return ApiResponse(data=data, meta=build_meta(request))


@router.post("/ingest", response_model=ApiResponse[IngestResponse])
async def ingest_route(
    request: Request,
    files: list[UploadFile] = File(...),
    collection_name: str = Form(...),
    chunk_size: int = Form(512, ge=64, le=4096),
    chunk_overlap: int = Form(64, ge=0, le=1024),
    db: AsyncSession = Depends(get_db),
):
    if chunk_overlap >= chunk_size:
        return error_response(
            code="INVALID_REQUEST",
            message="chunk_overlap must be smaller than chunk_size.",
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not files:
        return error_response(
            code="INVALID_REQUEST",
            message="At least one file must be uploaded.",
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with TemporaryDirectory() as temp_dir:
            file_paths: list[Path] = []
            for upload in files:
                filename = Path(upload.filename or "upload.bin").name
                file_path = Path(temp_dir) / filename
                content = await upload.read()
                file_path.write_bytes(content)
                file_paths.append(file_path)

            result = await ingest_documents(
                file_paths=file_paths,
                collection_name=collection_name,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                db=db,
            )
    except ValueError as exc:
        return error_response(
            code="INVALID_REQUEST",
            message=str(exc),
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except RuntimeError as exc:
        return error_response(
            code="INTERNAL_ERROR",
            message=str(exc),
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception:
        return error_response(
            code="INTERNAL_ERROR",
            message="Unexpected ingestion failure.",
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return ApiResponse(data=result, meta=build_meta(request))


@router.post("/query", dependencies=[Depends(check_rate_limit)])
async def query_route(
    request: Request,
    payload: QueryRequest,
    db: AsyncSession = Depends(get_db),
):
    started_at = perf_counter()
    request_id = getattr(request.state, "request_id", "unknown")

    result = await db.execute(select(RagCollection).where(RagCollection.id == payload.collection_id))
    collection = result.scalars().first()
    if collection is None:
        return error_response(
            code="COLLECTION_NOT_FOUND",
            message="The requested collection does not exist.",
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Semantic cache lookup
    cache_entry = await get_cached_response(payload.query)
    if cache_entry is not None:
        RAG_CACHE_HITS.inc()
        return StreamingResponse(
            replay_cached_sse(cache_entry, request_id=request_id, started_at=started_at, model=payload.model),
            media_type="text/event-stream",
            headers={**_SSE_HEADERS, "X-Cache": "HIT"},
        )
    RAG_CACHE_MISSES.inc()

    try:
        chunks = await retrieve_chunks(
            query=payload.query,
            collection_name=collection.qdrant_collection_name,
            top_k=payload.top_k,
            use_reranker=payload.use_reranker,
        )
    except ValueError as exc:
        return error_response(
            code="INVALID_REQUEST",
            message=str(exc),
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except RuntimeError as exc:
        return error_response(
            code="INTERNAL_ERROR",
            message=str(exc),
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    raw_gen = await stream_rag_response(
        query=payload.query,
        chunks=chunks,
        model=payload.model,
        request_id=request_id,
        started_at=started_at,
    )
    caching_gen = await capturing_sse_stream(raw_gen, query=payload.query)

    return StreamingResponse(
        caching_gen,
        media_type="text/event-stream",
        headers={**_SSE_HEADERS, "X-Cache": "MISS"},
    )
