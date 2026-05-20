"""Celery application with task definitions for background agent execution."""
from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "genai_forge",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    worker_prefetch_multiplier=1,  # prevent task starvation on single worker
    task_acks_late=True,
)
