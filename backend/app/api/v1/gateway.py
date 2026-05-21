"""API Gateway control endpoints — cache stats, rate-limit info, and API key management."""
import hashlib
import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.db import ApiKey

router = APIRouter(prefix="/gateway", tags=["gateway"])

_KEY_PREFIX_LENGTH = 8  # characters shown in the prefix (e.g., gf_abc12345)


def _generate_api_key() -> tuple[str, str, str]:
    """Return (raw_key, prefix, sha256_hex)."""
    raw = "gf_" + secrets.token_urlsafe(32)
    prefix = raw[:_KEY_PREFIX_LENGTH + 3]  # "gf_" + 8 chars
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    return raw, prefix, key_hash


@router.get("/stats")
async def gateway_stats():
    """Return live cache hit/miss totals and rate-limit config from in-process metrics."""
    from app.config import get_settings
    from app.observability.metrics import RAG_CACHE_HITS, RAG_CACHE_MISSES

    settings = get_settings()
    hits = RAG_CACHE_HITS._value.get()  # type: ignore[attr-defined]
    misses = RAG_CACHE_MISSES._value.get()  # type: ignore[attr-defined]
    total = hits + misses
    hit_rate = (hits / total * 100) if total > 0 else 0.0

    return {
        "cache": {
            "hits": int(hits),
            "misses": int(misses),
            "total": int(total),
            "hit_rate_pct": round(hit_rate, 2),
        },
        "rate_limit": {
            "rpm": settings.rate_limit_rpm,
            "window_seconds": 60,
        },
    }


class CreateKeyRequest(BaseModel):
    name: str


@router.post("/keys", status_code=status.HTTP_201_CREATED)
async def create_api_key(payload: CreateKeyRequest, db: AsyncSession = Depends(get_db)):
    """Generate a new API key. The raw key is returned ONCE and never stored."""
    raw_key, prefix, key_hash = _generate_api_key()
    api_key = ApiKey(name=payload.name, key_prefix=prefix, key_hash=key_hash)
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return {
        "id": str(api_key.id),
        "name": api_key.name,
        "key": raw_key,  # shown only once
        "prefix": prefix,
        "created_at": api_key.created_at.isoformat(),
    }


@router.get("/keys")
async def list_api_keys(db: AsyncSession = Depends(get_db)):
    """List active API keys — raw keys are never returned, only prefix and metadata."""
    result = await db.execute(
        select(ApiKey).where(ApiKey.is_active == True).order_by(ApiKey.created_at.desc())  # noqa: E712
    )
    keys = result.scalars().all()
    return [
        {
            "id": str(k.id),
            "name": k.name,
            "prefix": k.key_prefix + "…",
            "created_at": k.created_at.isoformat(),
        }
        for k in keys
    ]


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(key_id: UUID, db: AsyncSession = Depends(get_db)):
    """Soft-delete (deactivate) an API key by ID."""
    key = await db.get(ApiKey, key_id)
    if key is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"API key '{key_id}' not found."},
        )
    key.is_active = False
    await db.commit()
