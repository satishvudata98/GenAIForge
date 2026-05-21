"""OpenTelemetry setup — OTLP exporter to Jaeger, auto-instrumentation for FastAPI/SQLAlchemy/Redis."""
import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger("genai_forge.otel")


def setup_tracing(service_name: str, otlp_endpoint: str) -> None:
    """Initialize the global OTLP tracer provider and register auto-instrumentors."""
    resource = Resource.create({SERVICE_NAME: service_name})
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    logger.info("OpenTelemetry tracer configured → %s", otlp_endpoint)


def instrument_fastapi(app) -> None:
    """Attach FastAPI and SQLAlchemy instrumentors to the running app."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        SQLAlchemyInstrumentor().instrument()
        logger.info("FastAPI + SQLAlchemy OpenTelemetry instrumentation enabled.")
    except ImportError as exc:
        logger.warning("OTel FastAPI/SQLAlchemy packages missing — skipping: %s", exc)


def instrument_redis() -> None:
    """Attach Redis instrumentor (call once at startup)."""
    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        RedisInstrumentor().instrument()
        logger.info("Redis OpenTelemetry instrumentation enabled.")
    except ImportError as exc:
        logger.warning("OTel Redis package missing — skipping: %s", exc)


def instrument_celery() -> None:
    """Attach Celery instrumentor (call in celery_app.py after app creation)."""
    try:
        from opentelemetry.instrumentation.celery import CeleryInstrumentor

        CeleryInstrumentor().instrument()
        logger.info("Celery OpenTelemetry instrumentation enabled.")
    except ImportError as exc:
        logger.warning("OTel Celery package missing — skipping: %s", exc)
