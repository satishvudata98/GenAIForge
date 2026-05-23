"""Agent API routes — research (Day 10) and code review with HITL (Day 11)."""
import json
import logging
import uuid
from time import perf_counter

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from langgraph.types import Command
from pydantic import BaseModel

from app.models.schemas import SseEvent
from app.observability.metrics import ACTIVE_AGENT_RUNS, AGENT_RUNS_TOTAL

logger = logging.getLogger("genai_forge.agents")

router = APIRouter(prefix="/agents", tags=["agents"])

_SSE_MEDIA_TYPE = "text/event-stream"
_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _sse(event: SseEvent) -> str:
    return f"data: {json.dumps(event.model_dump(mode='json'))}\n\n"


# ── Request / Response schemas ────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    query: str
    model: str = "gpt-4o-mini"


class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"
    model: str = "gpt-4o-mini"


class ResumeRequest(BaseModel):
    feedback: str


# ── Research Agent ────────────────────────────────────────────────────────────

@router.post("/research")
async def research_route(request: Request, payload: ResearchRequest):
    """Stream research agent node events via SSE."""
    from app.agents.research_agent import research_graph
    from app.agents.state import ResearchState

    started_at = perf_counter()
    request_id = getattr(request.state, "request_id", "unknown")

    initial_state: ResearchState = {
        "query": payload.query,
        "plan": "",
        "search_results": [],
        "extracted_facts": [],
        "report": "",
        "messages": [],
        "current_node": "start",
        "error": None,
    }

    async def event_stream():
        ACTIVE_AGENT_RUNS.labels(agent_type="research").inc()
        AGENT_RUNS_TOTAL.labels(agent_type="research", status="started").inc()
        accumulated_report = ""
        try:
            async for chunk in research_graph.astream(initial_state, stream_mode="updates"):
                for node_name, node_output in chunk.items():
                    node_data = node_output.get("current_node", node_name)
                    yield _sse(SseEvent(
                        type="chunk",
                        content={"node": node_name, "data": node_data},
                    ))
                    # Accumulate from stream — avoids a second ainvoke() call
                    if node_output.get("report"):
                        accumulated_report = node_output["report"]

            yield _sse(SseEvent(type="source", content={"report": accumulated_report}))
            AGENT_RUNS_TOTAL.labels(agent_type="research", status="completed").inc()
        except Exception:
            logger.exception("Research agent error for request %s", request_id)
            AGENT_RUNS_TOTAL.labels(agent_type="research", status="error").inc()
            yield _sse(SseEvent(
                type="chunk",
                content={"node": "error", "data": "Research agent execution failed."},
            ))
        finally:
            ACTIVE_AGENT_RUNS.labels(agent_type="research").dec()

        latency_ms = int((perf_counter() - started_at) * 1000)
        yield _sse(SseEvent(
            type="meta",
            content={"request_id": request_id, "model": payload.model, "latency_ms": latency_ms},
        ))
        yield _sse(SseEvent(type="done"))

    return StreamingResponse(event_stream(), media_type=_SSE_MEDIA_TYPE, headers=_SSE_HEADERS)


# ── Code Review Agent (HITL) ──────────────────────────────────────────────────

# In-memory job registry for HITL resume; persisted via Postgres checkpointer in production
_hitl_jobs: dict[str, dict] = {}


@router.post("/code-review")
async def code_review_route(request: Request, payload: CodeReviewRequest):
    """Start a code review; streams events and pauses at the human-review node."""
    from app.agents.code_review_agent import get_code_review_graph
    from app.agents.state import CodeReviewState

    started_at = perf_counter()
    request_id = getattr(request.state, "request_id", "unknown")
    job_id = str(uuid.uuid4())

    graph = get_code_review_graph()
    config = {"configurable": {"thread_id": job_id}}

    initial_state: CodeReviewState = {
        "code": payload.code,
        "language": payload.language,
        "analysis": "",
        "security_issues": [],
        "suggestions": [],
        "human_feedback": None,
        "final_report": "",
        "messages": [],
        "current_node": "start",
        "approved": False,
        "job_id": job_id,
    }

    _hitl_jobs[job_id] = {"graph": graph, "config": config, "state": initial_state}

    async def event_stream():
        ACTIVE_AGENT_RUNS.labels(agent_type="code_review").inc()
        AGENT_RUNS_TOTAL.labels(agent_type="code_review", status="started").inc()
        try:
            async for chunk in graph.astream(
                initial_state, config=config, stream_mode="updates"
            ):
                for node_name, node_output in chunk.items():
                    yield _sse(SseEvent(
                        type="chunk",
                        content={"node": node_name, "job_id": job_id},
                    ))
                    if node_name == "suggest":
                        yield _sse(SseEvent(type="source", content={
                            "job_id": job_id,
                            "analysis": node_output.get("analysis", ""),
                            "security_issues": node_output.get("security_issues", []),
                            "suggestions": node_output.get("suggestions", []),
                        }))
        except Exception:
            logger.exception("Code review agent error for job %s", job_id)
            AGENT_RUNS_TOTAL.labels(agent_type="code_review", status="error").inc()
            yield _sse(SseEvent(
                type="chunk",
                content={"node": "error", "data": "Code review agent execution failed."},
            ))
        finally:
            ACTIVE_AGENT_RUNS.labels(agent_type="code_review").dec()

        latency_ms = int((perf_counter() - started_at) * 1000)
        yield _sse(SseEvent(
            type="meta",
            content={
                "request_id": request_id,
                "job_id": job_id,
                "latency_ms": latency_ms,
                "status": "awaiting_human_review",
            },
        ))
        yield _sse(SseEvent(type="done"))

    return StreamingResponse(event_stream(), media_type=_SSE_MEDIA_TYPE, headers=_SSE_HEADERS)


@router.post("/resume/{job_id}")
async def resume_route(job_id: str, payload: ResumeRequest, request: Request):
    """Resume a paused code-review graph with human feedback."""
    job = _hitl_jobs.get(job_id)
    if job is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {
                "code": "JOB_NOT_FOUND",
                "message": f"No active job with id '{job_id}'.",
            }},
        )

    graph = job["graph"]
    config = job["config"]

    async def event_stream():
        try:
            async for chunk in graph.astream(
                Command(resume=payload.feedback),
                config=config,
                stream_mode="updates",
            ):
                for node_name, _ in chunk.items():
                    yield _sse(SseEvent(
                        type="chunk",
                        content={"node": node_name, "job_id": job_id},
                    ))
        except Exception:
            logger.exception("Resume error for job %s", job_id)
            yield _sse(SseEvent(
                type="chunk",
                content={"node": "error", "data": "Agent resume execution failed."},
            ))

        _hitl_jobs.pop(job_id, None)
        yield _sse(SseEvent(type="meta", content={"job_id": job_id, "status": "complete"}))
        yield _sse(SseEvent(type="done"))

    return StreamingResponse(event_stream(), media_type=_SSE_MEDIA_TYPE, headers=_SSE_HEADERS)
