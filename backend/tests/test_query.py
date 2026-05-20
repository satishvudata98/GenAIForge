from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.dependencies import get_db
from app.main import create_app


class DummyResult:
    def __init__(self, collection):
        self._collection = collection

    def scalars(self):
        return self

    def first(self):
        return self._collection


class DummySession:
    def __init__(self, collection):
        self._collection = collection

    async def execute(self, _statement):
        return DummyResult(self._collection)


def make_db_override(collection):
    async def override_get_db():
        yield DummySession(collection)

    return override_get_db


def test_query_route_streams_sse(monkeypatch) -> None:
    collection = SimpleNamespace(id=uuid4(), qdrant_collection_name="kb-abcd1234")
    app = create_app()
    app.dependency_overrides[get_db] = make_db_override(collection)

    async def fake_retrieve_chunks(**kwargs):
        assert kwargs["collection_name"] == "kb-abcd1234"
        return [SimpleNamespace(to_source_payload=lambda: {"doc": "notes.md", "score": 0.98})]

    async def fake_stream_rag_response(**kwargs):
        assert kwargs["model"] == "gpt-4o-mini"
        yield 'data: {"type":"chunk","content":"hello","index":0}\n\n'
        yield 'data: {"type":"source","content":{"doc":"notes.md","score":0.98}}\n\n'
        yield 'data: {"type":"meta","content":{"model":"gpt-4o-mini"}}\n\n'
        yield 'data: {"type":"done","content":null,"index":null}\n\n'

    monkeypatch.setattr("app.api.v1.rag.retrieve_chunks", fake_retrieve_chunks)
    monkeypatch.setattr("app.api.v1.rag.stream_rag_response", fake_stream_rag_response)

    client = TestClient(app)
    response = client.post(
        "/v1/rag/query",
        json={
            "query": "What is GenAI Forge?",
            "collection_id": str(collection.id),
            "model": "gpt-4o-mini",
            "top_k": 5,
            "use_reranker": True,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-accel-buffering"] == "no"
    assert 'data: {"type":"chunk"' in response.text
    assert 'data: {"type":"source"' in response.text
    assert 'data: {"type":"meta"' in response.text
    assert 'data: {"type":"done"' in response.text


def test_query_route_returns_not_found() -> None:
    app = create_app()
    app.dependency_overrides[get_db] = make_db_override(None)
    client = TestClient(app)

    response = client.post(
        "/v1/rag/query",
        json={
            "query": "What is GenAI Forge?",
            "collection_id": str(uuid4()),
            "model": "gpt-4o-mini",
            "top_k": 5,
            "use_reranker": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "COLLECTION_NOT_FOUND"
