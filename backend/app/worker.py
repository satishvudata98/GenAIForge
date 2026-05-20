"""Entry-point re-export so docker-compose 'app.worker:celery_app' still resolves correctly."""
from app.workers.celery_app import celery_app  # noqa: F401

celery = celery_app
