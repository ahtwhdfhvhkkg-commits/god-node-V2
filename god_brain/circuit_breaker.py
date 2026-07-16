"""
circuit_breaker.py

Enterprise-grade Circuit Breaker, Retry Engine and Provider Health Monitor.

Features
--------
- Async-safe
- Exponential backoff with jitter
- Retry policy
- Provider health scoring
- Circuit Breaker (Closed / Open / Half-Open)
- Failure threshold
- Recovery timeout
- Success recovery
- Provider metrics
- Easy integration with aiohttp-based routers
"""

from __future__ import annotations

import asyncio
import enum
import logging
import random
import time

from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict, Optional, Tuple, TypeVar

logger = logging.getLogger("GodNode.CircuitBreaker")

T = TypeVar("T")


# ============================================================
# CIRCUIT STATES
# ============================================================

class CircuitState(str, enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass(slots=True)
class RetryConfig:
    max_attempts: int = 4
    base_delay: float = 1.0
    max_delay: float = 20.0
    exponential_base: float = 2.0
    jitter: bool = True

    retry_http_codes: Tuple[int, ...] = (
        429,
        500,
        502,
        503,
        504,
    )

    retry_exceptions: Tuple[type, ...] = (
        TimeoutError,
        asyncio.TimeoutError,
    )


@dataclass(slots=True)
class CircuitConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 180
    half_open_max_calls: int = 2
    success_threshold: int = 2


# ============================================================
# PROVIDER HEALTH
# ============================================================

@dataclass(slots=True)
class ProviderHealth:

    provider: str

    state: CircuitState = CircuitState.CLOSED

    score: float = 100.0

    successes: int = 0
    failures: int = 0

    consecutive_failures: int = 0
    consecutive_successes: int = 0

    total_requests: int = 0

    last_error: Optional[str] = None
    last_failure_time: float = 0.0

    opened_until: float = 0.0

    latency_ms: float = 0.0

    metadata: dict = field(default_factory=dict)


# ============================================================
# RETRY ENGINE
# ============================================================

class RetryEngine:

    def __init__(
        self,
        config: RetryConfig | None = None,
    ):

        self.config = config or RetryConfig()

    async def sleep(
        self,
        attempt: int,
    ):

        delay = min(
            self.config.base_delay *
            (self.config.exponential_base ** attempt),
            self.config.max_delay,
        )

        if self.config.jitter:
            delay += random.uniform(0.0, 0.5)

        await asyncio.sleep(delay)

    def should_retry_http(
        self,
        status: int,
    ) -> bool:

        return status in self.config.retry_http_codes

    def should_retry_exception(
        self,
        exc: Exception,
    ) -> bool:

        return isinstance(
            exc,
            self.config.retry_exceptions,
        )


# ============================================================
# CIRCUIT BREAKER
# ============================================================

class ProviderCircuitBreaker:

    def __init__(
        self,
        provider: str,
        config: CircuitConfig | None = None,
    ):

        self.provider = provider
        self.config = config or CircuitConfig()

        self.health = ProviderHealth(
            provider=provider
        )

        self._lock = asyncio.Lock()

    # --------------------------------------------------------

    async def allow_request(self) -> bool:

        async with self._lock:

            now = time.time()

            if self.health.state == CircuitState.OPEN:

                if now >= self.health.opened_until:

                    logger.warning(
                        "%s entering HALF_OPEN",
                        self.provider,
                    )

                    self.health.state = CircuitState.HALF_OPEN

                    self.health.consecutive_successes = 0

                    return True

                return False

            return True

    # --------------------------------------------------------

    async def on_success(
        self,
        latency_ms: float = 0,
    ):

        async with self._lock:

            self.health.total_requests += 1

            self.health.successes += 1

            self.health.latency_ms = latency_ms

            self.health.consecutive_successes += 1

            self.health.consecutive_failures = 0

            self.health.score = min(
                100,
                self.health.score + 2,
            )

            if self.health.state == CircuitState.HALF_OPEN:

                if (
                    self.health.consecutive_successes
                    >= self.config.success_threshold
                ):

                    logger.info(
                        "%s recovered.",
                        self.provider,
                    )

                    self.health.state = CircuitState.CLOSED

    # --------------------------------------------------------

    async def on_failure(
        self,
        reason: str,
    ):

        async with self._lock:

            self.health.total_requests += 1

            self.health.failures += 1

            self.health.last_error = reason

            self.health.last_failure_time = time.time()

            self.health.consecutive_failures += 1

            self.health.consecutive_successes = 0

            self.health.score = max(
                0,
                self.health.score - 10,
            )

            if (
                self.health.consecutive_failures
                >= self.config.failure_threshold
            ):

                logger.error(
                    "%s circuit OPEN.",
                    self.provider,
                )

                self.health.state = CircuitState.OPEN

                self.health.opened_until = (
                    time.time()
                    + self.config.recovery_timeout
                )

    # --------------------------------------------------------

    def snapshot(self) -> ProviderHealth:
        return self.health


# ============================================================
# REGISTRY
# ============================================================

class CircuitRegistry:

    def __init__(self):

        self._providers: Dict[
            str,
            ProviderCircuitBreaker,
        ] = {}

    def register(
        self,
        provider: str,
    ) -> ProviderCircuitBreaker:

        if provider not in self._providers:

            self._providers[provider] = (
                ProviderCircuitBreaker(provider)
            )

        return self._providers[provider]

    def get(
        self,
        provider: str,
    ) -> ProviderCircuitBreaker:

        return self.register(provider)

    def health(self):

        return {
            name: breaker.snapshot()
            for name, breaker
            in self._providers.items()
        }


# ============================================================
# EXECUTION WRAPPER
# ============================================================

class ProviderExecutor:

    def __init__(
        self,
        registry: CircuitRegistry,
        retry: RetryEngine | None = None,
    ):

        self.registry = registry

        self.retry = retry or RetryEngine()

    async def execute(
        self,
        provider: str,
        operation: Callable[[], Awaitable[T]],
    ) -> T:

        breaker = self.registry.get(provider)

        if not await breaker.allow_request():

            raise RuntimeError(
                f"{provider} circuit is OPEN."
            )

        for attempt in range(
            self.retry.config.max_attempts
        ):

            started = time.perf_counter()

            try:

                result = await operation()

                elapsed = (
                    time.perf_counter()
                    - started
                ) * 1000

                await breaker.on_success(elapsed)

                return result

            except Exception as exc:

                message = str(exc)

                status = getattr(
                    exc,
                    "status",
                    None,
                )

                retryable = False

                if (
                    status is not None
                    and self.retry.should_retry_http(
                        status
                    )
                ):
                    retryable = True

                if self.retry.should_retry_exception(
                    exc
                ):
                    retryable = True

                if (
                    attempt
                    >= self.retry.config.max_attempts
                    - 1
                ):

                    await breaker.on_failure(
                        message
                    )

                    raise

                if retryable:

                    logger.warning(
                        "%s retry %d/%d",
                        provider,
                        attempt + 1,
                        self.retry.config.max_attempts,
                    )

                    await self.retry.sleep(
                        attempt
                    )

                    continue

                await breaker.on_failure(
                    message
                )

                raise


# ============================================================
# GLOBAL SINGLETONS
# ============================================================

CIRCUIT_REGISTRY = CircuitRegistry()

RETRY_ENGINE = RetryEngine()

PROVIDER_EXECUTOR = ProviderExecutor(
    CIRCUIT_REGISTRY,
    RETRY_ENGINE,
)
