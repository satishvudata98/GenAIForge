from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
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


@router.post("/query")
async def query_route(
    request: Request,
    payload: QueryRequest,
    db: AsyncSession = Depends(get_db),
):
    started_at = perf_counter()

    result = await db.execute(select(RagCollection).where(RagCollection.id == payload.collection_id))
    collection = result.scalars().first()
    if collection is None:
        return error_response(
            code="COLLECTION_NOT_FOUND",
            message="The requested collection does not exist.",
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
        )

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

    async def event_stream():
        async for event in stream_rag_response(
            query=payload.query,
            chunks=chunks,
            model=payload.model,
            request_id=getattr(request.state, "request_id", "unknown"),
            started_at=started_at,
        ):
            yield event

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
