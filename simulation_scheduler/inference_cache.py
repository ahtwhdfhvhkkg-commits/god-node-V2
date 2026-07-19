"""
simulation_scheduler/inference_cache.py

Lightweight semantic inference cache with TTL and bounded memory usage.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Hashable, Optional

from .config import MemoryBudget, SchedulerConfig


@dataclass(slots=True)
class CacheEntry:
    """
    Cached inference result.
    """

    value: Any
    expires_at: float


class SemanticCache:
    """
    A lightweight TTL + LRU cache for semantic inference results.

    Features
    --------
    - O(1) lookup
    - O(1) insert
    - TTL expiration
    - LRU eviction
    - Memory bounded by MemoryBudget.max_cached_results
    """

    __slots__ = (
        "_enabled",
        "_ttl_seconds",
        "_capacity",
        "_cache",
    )

    def __init__(
        self,
        scheduler_config: SchedulerConfig,
        memory_budget: MemoryBudget,
    ) -> None:
        self._enabled = scheduler_config.enable_inference_cache
        self._ttl_seconds = scheduler_config.cache_ttl_seconds
        self._capacity = memory_budget.max_cached_results
        self._cache: OrderedDict[
            Hashable,
            CacheEntry,
        ] = OrderedDict()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def ttl_seconds(self) -> int:
        return self._ttl_seconds

    def __len__(self) -> int:
        return len(self._cache)

    def clear(self) -> None:
        """
        Remove every cached entry.
        """
        self._cache.clear()

    def contains(self, key: Hashable) -> bool:
        """
        Return True if a valid cache entry exists.
        """
        return self.get(key) is not None

    def get(
        self,
        key: Hashable,
    ) -> Optional[Any]:
        """
        Retrieve a cached value.

        Returns None if:
        - cache is disabled
        - key is missing
        - entry expired
        """
        if not self._enabled:
            return None

        entry = self._cache.get(key)

        if entry is None:
            return None

        now = time.monotonic()

        if entry.expires_at <= now:
            del self._cache[key]
            return None

        # Maintain LRU ordering.
        self._cache.move_to_end(key)

        return entry.value

    def put(
        self,
        key: Hashable,
        value: Any,
    ) -> None:
        """
        Insert or replace a cached value.
        """
        if not self._enabled:
            return

        now = time.monotonic()

        if key in self._cache:
            self._cache.move_to_end(key)

        self._cache[key] = CacheEntry(
            value=value,
            expires_at=now + self._ttl_seconds,
        )

        while len(self._cache) > self._capacity:
            self._cache.popitem(last=False)

    def remove(
        self,
        key: Hashable,
    ) -> bool:
        """
        Remove a cached entry.

        Returns True if an entry existed.
        """
        return self._cache.pop(key, None) is not None

    def cleanup(self) -> int:
        """
        Remove expired entries.

        Returns
        -------
        int
            Number of removed entries.
        """
        if not self._cache:
            return 0

        now = time.monotonic()
        removed = 0

        expired_keys = [
            key
            for key, entry in self._cache.items()
            if entry.expires_at <= now
        ]

        for key in expired_keys:
            del self._cache[key]
            removed += 1

        return removed

    def stats(self) -> dict[str, int]:
        """
        Return basic cache statistics.
        """
        return {
            "entries": len(self._cache),
            "capacity": self._capacity,
}
