"""
routing_policy.py

Pure architectural components for God Node.

This module intentionally contains:
- Health-based provider selection logic
- Request normalization interfaces
- Abstract adapter skeletons

It intentionally DOES NOT contain:
- External API calls
- HTTP execution
- Provider-specific implementations
- API endpoint wiring
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Protocol

from .circuit_breaker import CIRCUIT_REGISTRY
from .provider_sdk import PromptRequest


# ============================================================
# ENUMS
# ============================================================

class ProviderCapability(str, Enum):
    GENERAL = "general"
    CHAT = "chat"
    CODE = "code"
    REASONING = "reasoning"
    CREATIVE = "creative"
    TOOLS = "tools"
    EMBEDDING = "embedding"
    AUDIO = "audio"
    VISION = "vision"


# ============================================================
# ROUTING REQUEST
# ============================================================

@dataclass(slots=True)
class RoutingRequest:

    prompt: PromptRequest

    required_capabilities: set[ProviderCapability] = field(
        default_factory=set
    )

    preferred_provider: Optional[str] = None

    excluded_providers: set[str] = field(
        default_factory=set
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# PROVIDER DESCRIPTOR
# ============================================================

@dataclass(slots=True)
class ProviderDescriptor:

    name: str

    enabled: bool = True

    priority: int = 100

    capabilities: set[ProviderCapability] = field(
        default_factory=set
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# NORMALIZED PAYLOAD
# ============================================================

@dataclass(slots=True)
class NormalizedPayload:

    body: Dict[str, Any]

    headers: Dict[str, str] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# PAYLOAD BUILDER PROTOCOL
# ============================================================

class PayloadBuilder(Protocol):

    def build(
        self,
        request: RoutingRequest,
    ) -> NormalizedPayload:
        ...


# ============================================================
# ABSTRACT NORMALIZER
# ============================================================

class RequestNormalizer(ABC):

    @abstractmethod
    def normalize(
        self,
        request: RoutingRequest,
    ) -> NormalizedPayload:
        ...


# ============================================================
# BASE ADAPTER SKELETON
# ============================================================

class ProviderAdapterSkeleton(RequestNormalizer):

    def __init__(
        self,
        descriptor: ProviderDescriptor,
    ):

        self.descriptor = descriptor

    def normalize(
        self,
        request: RoutingRequest,
    ) -> NormalizedPayload:

        return self.build_payload(request)

    @abstractmethod
    def build_payload(
        self,
        request: RoutingRequest,
    ) -> NormalizedPayload:
        ...


# ============================================================
# DEFAULT GENERIC ADAPTER
# ============================================================

class GenericJSONAdapter(
    ProviderAdapterSkeleton
):

    def build_payload(
        self,
        request: RoutingRequest,
    ) -> NormalizedPayload:

        payload = {
            "prompt": request.prompt.prompt,
            "system_prompt": request.prompt.system_prompt,
            "temperature": request.prompt.temperature,
            "max_tokens": request.prompt.max_tokens,
            "metadata": request.prompt.metadata,
        }

        return NormalizedPayload(
            body=payload
        )


# ============================================================
# ROUTING POLICY
# ============================================================

class HealthRoutingPolicy:

    """
    Pure health-based provider selector.

    Uses provider health snapshots only.

    No execution logic.
    """

    def select_provider(
        self,
        providers: Iterable[ProviderDescriptor],
        request: RoutingRequest,
    ) -> Optional[str]:

        provider_list = list(providers)

        if request.preferred_provider:

            for provider in provider_list:

                if (
                    provider.enabled
                    and provider.name
                    == request.preferred_provider
                ):
                    return provider.name

        candidates: List[tuple] = []

        registry = CIRCUIT_REGISTRY.health()

        for provider in provider_list:

            if not provider.enabled:
                continue

            if provider.name in request.excluded_providers:
                continue

            if (
                request.required_capabilities
                and not request.required_capabilities.issubset(
                    provider.capabilities
                )
            ):
                continue

            health = registry.get(provider.name)

            if health is None:

                score = 100.0

                state = "closed"

            else:

                score = health.score

                state = health.state.value

            if state == "open":
                continue

            candidates.append(
                (
                    score,
                    provider.priority,
                    provider.name,
                )
            )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: (
                item[0],
                item[1],
            ),
            reverse=True,
        )

        return candidates[0][2]


# ============================================================
# REGISTRY
# ============================================================

class ProviderCatalog:

    def __init__(self):

        self._providers: Dict[
            str,
            ProviderDescriptor,
        ] = {}

    def register(
        self,
        provider: ProviderDescriptor,
    ) -> None:

        self._providers[
            provider.name
        ] = provider

    def unregister(
        self,
        provider_name: str,
    ) -> None:

        self._providers.pop(
            provider_name,
            None,
        )

    def get(
        self,
        provider_name: str,
    ) -> Optional[ProviderDescriptor]:

        return self._providers.get(
            provider_name
        )

    def all(
        self,
    ) -> List[ProviderDescriptor]:

        return list(
            self._providers.values()
        )

    def enabled(
        self,
    ) -> List[ProviderDescriptor]:

        return [
            provider
            for provider in self._providers.values()
            if provider.enabled
        ]

    def as_mapping(
        self,
    ) -> Mapping[str, ProviderDescriptor]:

        return dict(
            self._providers
        )


# ============================================================
# FACADE
# ============================================================

class RoutingPolicy:

    def __init__(self):

        self.catalog = ProviderCatalog()

        self.policy = HealthRoutingPolicy()

    def register(
        self,
        provider: ProviderDescriptor,
    ) -> None:

        self.catalog.register(provider)

    def choose(
        self,
        request: RoutingRequest,
    ) -> Optional[str]:

        return self.policy.select_provider(
            self.catalog.enabled(),
            request,
        )


DEFAULT_ROUTING_POLICY = RoutingPolicy()
