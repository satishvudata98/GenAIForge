import logging
import time
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from opentelemetry import trace
from redis.asyncio import Redis

from app.config import get_settings
from app.observability.metrics import REQUEST_COUNT, REQUEST_LATENCY

settings = get_settings()

logger = logging.getLogger("genai_forge.request")

_rate_limit_redis: Redis | None = None


def _get_rate_limit_redis() -> Redis:
    global _rate_limit_redis
    if _rate_limit_redis is None:
        _rate_limit_redis = Redis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )
    return _rate_limit_redis


async def check_rate_limit(request: Request) -> None:
    """FastAPI dependency — raises HTTP 429 when client exceeds rate_limit_rpm.

    Skips enforcement gracefully when Redis is unavailable.
    """
    redis = _get_rate_limit_redis()
    client_id = (
        request.headers.get("x-api-key")
        or (request.client.host if request.client else "anon")
    )
    window = int(time.time() // 60)
    key = f"rl:{client_id}:{window}"
    try:
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 60)
    except Exception:
        logger.warning("Rate-limit Redis unavailable — skipping enforcement for %s", client_id)
        return
    if count > settings.rate_limit_rpm:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit of {settings.rate_limit_rpm} RPM exceeded.",
            },
            headers={"Retry-After": "60"},
        )


def register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        start = perf_counter()
        request_id = request.headers.get("x-request-id") or f"req_{uuid4().hex}"
        request.state.request_id = request_id

        # Propagate request_id into the active OTel span
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute("request.id", request_id)

        response = await call_next(request)

        elapsed_ms = int((perf_counter() - start) * 1000)
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)

        REQUEST_COUNT.labels(
            method=request.method,
            path=route_path,
            status_code=str(response.status_code),
        ).inc()
        REQUEST_LATENCY.labels(method=request.method, path=route_path).observe(elapsed_ms / 1000)

        logger.info(
            "request_complete request_id=%s method=%s path=%s "
            "status_code=%s latency_ms=%s request_size=%s",
            request_id,
            request.method,
            route_path,
            response.status_code,
            elapsed_ms,
            request.headers.get("content-length", "0"),
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-MS"] = str(elapsed_ms)
        return response
