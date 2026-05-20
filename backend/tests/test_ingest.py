from uuid import uuid4

from fastapi.testclient import TestClient

from app.dependencies import get_db
from app.main import create_app
from app.models.schemas import IngestResponse


class DummySession:
    pass


async def override_get_db():
    yield DummySession()


def test_ingest_route_returns_envelope(monkeypatch) -> None:
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    async def fake_ingest_documents(**kwargs):
        assert kwargs["collection_name"] == "knowledge-base"
        assert kwargs["chunk_size"] == 512
        assert kwargs["chunk_overlap"] == 64
        assert len(kwargs["file_paths"]) == 1
        return IngestResponse(
            collection_id=uuid4(),
            collection_name="knowledge-base",
            qdrant_collection_name="knowledge-base-abcd1234",
            documents_ingested=1,
            chunks_indexed=3,
            embedding_model="text-embedding-3-large",
        )

    monkeypatch.setattr("app.api.v1.rag.ingest_documents", fake_ingest_documents)

    client = TestClient(app)
    response = client.post(
        "/v1/rag/ingest",
        data={
            "collection_name": "knowledge-base",
            "chunk_size": "512",
            "chunk_overlap": "64",
        },
        files={"files": ("notes.md", b"Hello world", "text/markdown")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["collection_name"] == "knowledge-base"
    assert body["data"]["chunks_indexed"] == 3
    assert body["meta"]["request_id"].startswith("req_")


def test_ingest_route_rejects_invalid_overlap() -> None:
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/v1/rag/ingest",
        data={
            "collection_name": "knowledge-base",
            "chunk_size": "64",
            "chunk_overlap": "64",
        },
        files={"files": ("notes.md", b"Hello world", "text/markdown")},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "INVALID_REQUEST"
