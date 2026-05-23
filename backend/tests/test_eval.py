"""Tests for RAGAS evaluation endpoints."""
import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_db
from app.main import create_app
from app.models.db import EvalRun

CSV_CONTENT = (
    b"question,answer,contexts,ground_truth\n"
    b"What is X?,X is a thing.,Context about X.,X is a thing.\n"
)


class DummyEvalResult:
    def __init__(self, runs):
        self._runs = runs

    def scalars(self):
        return self

    def all(self):
        return self._runs


class DummyEvalSession:
    def __init__(self, runs=None):
        self._runs = runs or []
        self.added = []

    async def execute(self, _stmt):
        await asyncio.sleep(0)  # yields control — satisfies async interface
        return DummyEvalResult(self._runs)

    def add(self, obj):
        self.added.append(obj)

    async def commit(self) -> None:
        await asyncio.sleep(0)  # no-op: test double does not persist

    async def refresh(self, obj) -> None:
        await asyncio.sleep(0)  # no-op: test double skips DB refresh
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = uuid4()


def _make_override(session):
    async def override():
        yield session

    return override


def test_start_eval_run_accepts_csv(monkeypatch) -> None:
    from unittest.mock import MagicMock

    app = create_app()
    session = DummyEvalSession()
    app.dependency_overrides[get_db] = _make_override(session)

    def fake_create_task(coro):
        coro.close()  # prevent "coroutine never awaited" warning
        return MagicMock()

    monkeypatch.setattr("app.api.v1.eval.asyncio.create_task", fake_create_task)

    client = TestClient(app)
    response = client.post(
        "/v1/eval/run",
        data={"dataset_name": "test-dataset"},
        files={"file": ("eval.csv", CSV_CONTENT, "text/csv")},
    )

    assert response.status_code == 202
    body = response.json()
    assert "run_id" in body
    assert body["status"] == "running"
    assert body["dataset_name"] == "test-dataset"


def test_start_eval_run_rejects_non_csv() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/v1/eval/run",
        data={"dataset_name": "bad"},
        files={"file": ("data.txt", b"not csv", "text/plain")},
    )

    assert response.status_code == 400


def test_list_eval_results_returns_list() -> None:
    run = EvalRun(
        id=uuid4(),
        dataset_name="my-dataset",
        status="completed",
        faithfulness=0.9,
        answer_relevancy=0.85,
        context_precision=0.88,
        context_recall=0.82,
        row_count=10,
    )
    run.created_at = datetime.now(UTC)

    app = create_app()
    session = DummyEvalSession(runs=[run])
    app.dependency_overrides[get_db] = _make_override(session)

    client = TestClient(app)
    response = client.get("/v1/eval/results")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["dataset_name"] == "my-dataset"
    assert body[0]["faithfulness"] == pytest.approx(0.9)
