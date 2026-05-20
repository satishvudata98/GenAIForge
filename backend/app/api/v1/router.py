from fastapi import APIRouter

from app.api.v1.agents import router as agents_router
from app.api.v1.health import router as health_router
from app.api.v1.rag import router as rag_router
from app.api.v1.workers import router as workers_router

router = APIRouter()
router.include_router(health_router)
router.include_router(rag_router)
router.include_router(agents_router)
router.include_router(workers_router)
