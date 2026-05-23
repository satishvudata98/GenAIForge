"""Tests for agent API routes — research, code-review, and resume."""
import json
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import create_app


def _parse_sse(text: str) -> list[dict]:
    events = []
    for line in text.split("\n\n"):
        line = line.strip()
        if line.startswith("data: "):
            try:
                events.append(json.loads(line[6:]))
            except json.JSONDecodeError:
                pass
    return events


def test_research_route_streams_sse(monkeypatch) -> None:
    app = create_app()

    async def fake_astream(state, stream_mode=None):
        yield {"plan": {"current_node": "plan", "report": ""}}
        yield {"synthesize": {"current_node": "synthesize", "report": "Fake research report."}}

    fake_graph = MagicMock()
    fake_graph.astream = fake_astream

    # Patch the source module attribute — the route uses a deferred import each call
    monkeypatch.setattr("app.agents.research_agent.research_graph", fake_graph)

    client = TestClient(app)
    response = client.post(
        "/v1/agents/research",
        json={"query": "What is LangGraph?", "model": "gpt-4o-mini"},
    )

    assert response.status_code == 200
    assert response.headers["x-accel-buffering"] == "no"

    events = _parse_sse(response.text)
    types = [e["type"] for e in events]
    assert "chunk" in types
    assert "source" in types
    assert "meta" in types
    assert "done" in types

    # Confirm report extracted from stream — no second ainvoke call
    source_event = next(e for e in events if e["type"] == "source")
    assert source_event["content"]["report"] == "Fake research report."


def test_code_review_route_streams_sse(monkeypatch) -> None:
    app = create_app()

    async def fake_astream(state, config=None, stream_mode=None):
        yield {"analyze": {"current_node": "analyze"}}
        yield {"suggest": {
            "current_node": "suggest",
            "analysis": "Looks good.",
            "security_issues": [],
            "suggestions": ["Add types."],
        }}

    fake_graph = MagicMock()
    fake_graph.astream = fake_astream

    monkeypatch.setattr("app.agents.code_review_agent.get_code_review_graph", lambda: fake_graph)

    client = TestClient(app)
    response = client.post(
        "/v1/agents/code-review",
        json={"code": "def foo(): pass", "language": "python", "model": "gpt-4o-mini"},
    )

    assert response.status_code == 200
    events = _parse_sse(response.text)
    types = [e["type"] for e in events]
    assert "chunk" in types
    assert "source" in types
    assert "meta" in types
    assert "done" in types

    meta_event = next(e for e in events if e["type"] == "meta")
    assert "job_id" in meta_event["content"]
    assert meta_event["content"]["status"] == "awaiting_human_review"


def test_resume_route_404_for_unknown_job() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/v1/agents/resume/nonexistent-job-id",
        json={"feedback": "looks fine"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "JOB_NOT_FOUND"
