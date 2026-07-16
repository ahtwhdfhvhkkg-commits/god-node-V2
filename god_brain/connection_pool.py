"""
connection_pool.py

Enterprise-grade HTTP Connection Pool & TTL Cache

Features
--------
- Shared aiohttp.ClientSession
- TCP connection pooling
- DNS cache
- HTTP keep-alive
- Graceful startup / shutdown
- Async-safe TTL cache
- Model discovery cache
- Generic async cache API
- Production logging
"""

from __future__ import annotations

import asyncio
import logging
import ssl
import time
from dataclasses import dataclass
from typing import Any, Dict, Generic, Optional, TypeVar

import aiohttp

logger = logging.getLogger("GodNode.ConnectionPool")

T = TypeVar("T")


# ============================================================
# TTL CACHE
# ============================================================

@dataclass(slots=True)
class CacheEntry(Generic[T]):
    value: T
    expires_at: float


class AsyncTTLCache(Generic[T]):
    """
    Async-safe in-memory TTL cache.

    Thread-safe for asyncio applications.
    """

    def __init__(self, ttl_seconds: int = 3600):
        self._ttl = ttl_seconds
        self._cache: Dict[str, CacheEntry[T]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[T]:
        async with self._lock:

            entry = self._cache.get(key)

            if entry is None:
                return None

            if entry.expires_at <= time.time():
                self._cache.pop(key, None)
                return None

            return entry.value

    async def set(
        self,
        key: str,
        value: T,
        ttl: Optional[int] = None,
    ) -> None:

        expiration = time.time() + (ttl or self._ttl)

        async with self._lock:
            self._cache[key] = CacheEntry(
                value=value,
                expires_at=expiration,
            )

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()

    async def contains(self, key: str) -> bool:
        return await self.get(key) is not None

    async def cleanup(self) -> None:
        now = time.time()

        async with self._lock:

            expired = [
                key
                for key, value in self._cache.items()
                if value.expires_at <= now
            ]

            for key in expired:
                self._cache.pop(key, None)

    async def size(self) -> int:
        async with self._lock:
            return len(self._cache)


# ============================================================
# SHARED HTTP CLIENT
# ============================================================

class SharedHTTPClient:
    """
    Global reusable aiohttp session.

    Use:

        await SharedHTTPClient.startup()

        session = SharedHTTPClient.session()

        ...

        await SharedHTTPClient.shutdown()
    """

    _session: Optional[aiohttp.ClientSession] = None
    _lock = asyncio.Lock()

    DEFAULT_TIMEOUT = aiohttp.ClientTimeout(
        total=60,
        connect=10,
        sock_connect=10,
        sock_read=60,
    )

    @classmethod
    async def startup(cls) -> None:

        if cls._session is not None:
            return

        async with cls._lock:

            if cls._session is not None:
                return

            ssl_context = ssl.create_default_context()

            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=200,
                limit_per_host=50,
                ttl_dns_cache=600,
                use_dns_cache=True,
                enable_cleanup_closed=True,
                force_close=False,
                keepalive_timeout=120,
            )

            cls._session = aiohttp.ClientSession(
                connector=connector,
                timeout=cls.DEFAULT_TIMEOUT,
                trust_env=True,
                raise_for_status=False,
                headers={
                    "User-Agent": "GodNodeV2/Enterprise",
                    "Accept": "application/json",
                },
            )

            logger.info("Shared HTTP session initialized.")

    @classmethod
    async def shutdown(cls) -> None:

        async with cls._lock:

            if cls._session is None:
                return

            await cls._session.close()

            cls._session = None

            logger.info("Shared HTTP session closed.")

    @classmethod
    def session(cls) -> aiohttp.ClientSession:

        if cls._session is None:
            raise RuntimeError(
                "SharedHTTPClient.startup() has not been called."
            )

        return cls._session

    @classmethod
    def initialized(cls) -> bool:
        return cls._session is not None


# ============================================================
# MODEL DISCOVERY CACHE
# ============================================================

class ModelCache:
    """
    Provider model cache.

    Example:

        cache = ModelCache()

        await cache.set_models(
            "openai",
            ["gpt-5","gpt-4.1"],
        )

        models = await cache.get_models("openai")
    """

    def __init__(self, ttl_seconds: int = 3600):
        self._cache = AsyncTTLCache[list[str]](ttl_seconds)

    async def get_models(
        self,
        provider: str,
    ) -> Optional[list[str]]:

        return await self._cache.get(provider)

    async def set_models(
        self,
        provider: str,
        models: list[str],
        ttl: Optional[int] = None,
    ) -> None:

        await self._cache.set(
            provider,
            models,
            ttl,
        )

    async def invalidate(
        self,
        provider: str,
    ) -> None:

        await self._cache.delete(provider)

    async def clear(self) -> None:
        await self._cache.clear()


# ============================================================
# GLOBAL SINGLETONS
# ============================================================

MODEL_CACHE = ModelCache(ttl_seconds=3600)
HTTP_CLIENT = SharedHTTPClient


# ============================================================
# OPTIONAL LIFECYCLE HELPERS
# ============================================================

async def startup() -> None:
    """
    Call from FastAPI startup event.
    """
    await HTTP_CLIENT.startup()


async def shutdown() -> None:
    """
    Call from FastAPI shutdown event.
    """
    await HTTP_CLIENT.shutdown()
