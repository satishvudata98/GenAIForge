import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram

logger = logging.getLogger("genai_forge.request")

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the API.",
    labelnames=("method", "path", "status_code"),
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    labelnames=("method", "path"),
)


def register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        start = perf_counter()
        request_id = request.headers.get("x-request-id") or f"req_{uuid4().hex}"
        request.state.request_id = request_id

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
            "request_complete request_id=%s method=%s path=%s status_code=%s latency_ms=%s request_size=%s",
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
