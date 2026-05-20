"""Workers API routes — submit CrewAI jobs, stream progress via Redis pub/sub SSE."""
import asyncio
import json

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.models.schemas import SseEvent

router = APIRouter(prefix="/workers", tags=["workers"])


def _sse(event: SseEvent) -> str:
    return f"data: {json.dumps(event.model_dump(mode='json'))}\n\n"


class CrewPipelineRequest(BaseModel):
    topic: str
    model: str = "gpt-4o-mini"


class ResearchTaskRequest(BaseModel):
    query: str
    model: str = "gpt-4o-mini"


@router.post("/crew-pipeline")
async def submit_crew_pipeline(request: Request, payload: CrewPipelineRequest):
    """Submit a CrewAI content pipeline job and stream progress via SSE."""
    from app.workers.tasks import run_crew_pipeline_task

    task = run_crew_pipeline_task.apply_async(kwargs={"topic": payload.topic, "model": payload.model})

    async def event_stream():
        yield _sse(SseEvent(type="chunk", content={"task_id": task.id, "status": "PENDING", "topic": payload.topic}))

        while not task.ready():
            await asyncio.sleep(1)
            info = task.info or {}
            yield _sse(SseEvent(type="chunk", content={"task_id": task.id, "status": task.state, "step": info.get("step", "")}))

        if task.successful():
            result = task.result
            yield _sse(SseEvent(type="source", content={"task_id": task.id, "result": result}))
            yield _sse(SseEvent(type="meta", content={"task_id": task.id, "status": "SUCCESS"}))
        else:
            yield _sse(SseEvent(type="chunk", content={"task_id": task.id, "status": "FAILURE", "error": str(task.result)}))

        yield _sse(SseEvent(type="done"))

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.post("/research")
async def submit_research_task(request: Request, payload: ResearchTaskRequest):
    """Submit a background research agent task."""
    from app.workers.tasks import run_research_agent_task

    task = run_research_agent_task.apply_async(kwargs={"query": payload.query, "model": payload.model})
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"task_id": task.id, "status": "PENDING", "query": payload.query},
    )


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Poll Celery task status and result."""
    from celery.result import AsyncResult

    from app.workers.celery_app import celery_app

    result = AsyncResult(task_id, app=celery_app)
    response: dict = {"task_id": task_id, "status": result.state}
    if result.ready():
        if result.successful():
            response["result"] = result.result
        else:
            response["error"] = str(result.result)
    return JSONResponse(content=response)
