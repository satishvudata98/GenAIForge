"""Tests for API gateway endpoints — stats, key creation, listing, and revocation."""
import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.dependencies import get_db
from app.main import create_app
from app.models.db import ApiKey


class DummyKeyResult:
    def __init__(self, keys):
        self._keys = keys

    def scalars(self):
        return self

    def all(self):
        return self._keys


class DummyGatewaySession:
    def __init__(self, keys=None):
        self._keys = keys or []
        self._store: dict = {}

    async def execute(self, _stmt):
        await asyncio.sleep(0)  # yields control — satisfies async interface
        return DummyKeyResult(self._keys)

    def add(self, obj):
        obj.id = uuid4()
        self._store[str(obj.id)] = obj

    async def commit(self) -> None:
        await asyncio.sleep(0)  # no-op: test double does not persist

    async def refresh(self, obj) -> None:
        await asyncio.sleep(0)  # no-op: test double skips DB refresh
        if not hasattr(obj, "created_at") or obj.created_at is None:
            obj.created_at = datetime.now(UTC)

    async def get(self, model_cls, key_id):  # noqa: ARG002
        await asyncio.sleep(0)
        for obj in self._store.values():
            if str(obj.id) == str(key_id):
                return obj
        return None


def _make_override(session):
    async def override():
        yield session

    return override


def test_gateway_stats_returns_cache_info() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/v1/gateway/stats")

    assert response.status_code == 200
    body = response.json()
    assert "cache" in body
    assert "rate_limit" in body
    assert "hits" in body["cache"]
    assert "misses" in body["cache"]
    assert "hit_rate_pct" in body["cache"]
    assert "rpm" in body["rate_limit"]


def test_create_api_key_returns_raw_key() -> None:
    app = create_app()
    session = DummyGatewaySession()
    app.dependency_overrides[get_db] = _make_override(session)

    client = TestClient(app)
    response = client.post("/v1/gateway/keys", json={"name": "test-key"})

    assert response.status_code == 201
    body = response.json()
    assert body["key"].startswith("gf_")
    assert body["name"] == "test-key"
    assert "prefix" in body
    assert "id" in body


def test_list_api_keys_hides_raw_key() -> None:
    key = ApiKey(
        id=uuid4(),
        name="prod-key",
        key_prefix="gf_abc12345",
        key_hash="fakehash",
        is_active=True,
    )
    key.created_at = datetime.now(UTC)

    app = create_app()
    session = DummyGatewaySession(keys=[key])
    app.dependency_overrides[get_db] = _make_override(session)

    client = TestClient(app)
    response = client.get("/v1/gateway/keys")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert "key" not in body[0]
    assert body[0]["name"] == "prod-key"


def test_revoke_api_key_returns_204() -> None:
    key_id = uuid4()
    key = ApiKey(
        id=key_id,
        name="to-revoke",
        key_prefix="gf_del12345",
        key_hash="fakehash2",
        is_active=True,
    )
    key.created_at = datetime.now(UTC)

    app = create_app()
    session = DummyGatewaySession()
    session._store[str(key_id)] = key
    app.dependency_overrides[get_db] = _make_override(session)

    client = TestClient(app)
    response = client.delete(f"/v1/gateway/keys/{key_id}")

    assert response.status_code == 204
    assert key.is_active is False
