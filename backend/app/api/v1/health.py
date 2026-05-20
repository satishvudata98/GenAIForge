from asyncio import open_connection, wait_for
from urllib.parse import urlparse

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


class ResponseMeta(BaseModel):
    request_id: str


class HealthData(BaseModel):
    status: str
    service: str
    environment: str


class ReadinessCheck(BaseModel):
    service: str
    ok: bool
    detail: str


class ReadinessData(BaseModel):
    status: str
    checks: list[ReadinessCheck]


class HealthResponse(BaseModel):
    data: HealthData
    meta: ResponseMeta


class ReadinessResponse(BaseModel):
    data: ReadinessData
    meta: ResponseMeta


def build_meta(request: Request) -> ResponseMeta:
    return ResponseMeta(request_id=getattr(request.state, "request_id", "unknown"))


def default_port(parsed_url) -> int:
    if parsed_url.port:
        return parsed_url.port
    if parsed_url.scheme.startswith("postgres"):
        return 5432
    if parsed_url.scheme.startswith("redis"):
        return 6379
    return 80


async def check_tcp(service: str, target: str) -> ReadinessCheck:
    parsed_url = urlparse(target)
    host = parsed_url.hostname or "localhost"
    port = default_port(parsed_url)

    try:
        reader, writer = await wait_for(open_connection(host, port), timeout=1.0)
        writer.close()
        await writer.wait_closed()
    except Exception as exc:
        return ReadinessCheck(service=service, ok=False, detail=str(exc))

    return ReadinessCheck(service=service, ok=True, detail=f"connected to {host}:{port}")


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    return HealthResponse(
        data=HealthData(
            status="ok",
            service=settings.app_name,
            environment=settings.environment,
        ),
        meta=build_meta(request),
    )


@router.get("/readiness", response_model=ReadinessResponse)
async def readiness(request: Request):
    checks = [
        await check_tcp("postgres", settings.postgres_dsn),
        await check_tcp("redis", settings.redis_url),
        await check_tcp("qdrant", str(settings.qdrant_url)),
    ]
    all_ok = all(check.ok for check in checks)
    payload = ReadinessResponse(
        data=ReadinessData(status="ready" if all_ok else "degraded", checks=checks),
        meta=build_meta(request),
    )

    if all_ok:
        return payload

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload.model_dump(mode="json"),
    )
