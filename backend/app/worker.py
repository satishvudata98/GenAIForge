from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "genai_forge",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery = celery_app
