from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RedisCacheClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None
        self._unavailable_logged = False

    @property
    def enabled(self) -> bool:
        return self.settings.redis_enabled and bool(self.settings.redis_url.strip())

    async def get_json(self, key: str) -> Any | None:
        client = await self._get_client()
        if client is None:
            return None
        try:
            raw = await client.get(key)
        except Exception:
            logger.exception("Redis get failed for key=%s", key)
            return None
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Invalid Redis JSON payload for key=%s", key)
            return None

    async def set_json(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None:
        client = await self._get_client()
        if client is None:
            return
        try:
            payload = json.dumps(value, ensure_ascii=False, default=str)
            await client.set(key, payload, ex=ttl_seconds or self.settings.redis_default_ttl_seconds)
        except Exception:
            logger.exception("Redis set failed for key=%s", key)

    async def delete(self, *keys: str) -> None:
        if not keys:
            return
        client = await self._get_client()
        if client is None:
            return
        try:
            await client.delete(*keys)
        except Exception:
            logger.exception("Redis delete failed for keys=%s", keys)

    async def close(self) -> None:
        if self._client is None:
            return
        try:
            await self._client.aclose()
        except Exception:
            logger.exception("Redis client close failed.")
        finally:
            self._client = None

    async def _get_client(self):
        if not self.enabled:
            return None
        if self._client is not None:
            return self._client
        try:
            from redis import asyncio as redis_asyncio
        except ImportError:
            if not self._unavailable_logged:
                logger.warning("redis package not installed, Redis cache disabled.")
                self._unavailable_logged = True
            return None

        try:
            self._client = redis_asyncio.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._client.ping()
            return self._client
        except Exception:
            logger.exception("Redis connection failed, cache disabled for this process.")
            self._client = None
            return None


redis_cache_client = RedisCacheClient()
