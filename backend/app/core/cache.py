import json
from typing import Any

from redis.asyncio import Redis

from app.config import get_settings

settings = get_settings()


class RedisCache:
    def __init__(self, redis_url: str | None = None) -> None:
        self._client = Redis.from_url(
            redis_url or settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        payload = value if isinstance(value, str) else json.dumps(value)
        return bool(await self._client.set(key, payload, ex=ttl))

    async def delete(self, key: str) -> int:
        return int(await self._client.delete(key))

    async def close(self) -> None:
        await self._client.aclose()
