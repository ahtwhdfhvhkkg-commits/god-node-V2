"""
provider_sdk.py

Foundational provider SDK for God Node.

Purpose
-------
This module defines the provider configuration schema and the adapter
interfaces used by the routing engine.

The router should only depend on these interfaces.

No provider-specific logic belongs in this module.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Sequence

from connection_pool import HTTP_CLIENT
from circuit_breaker import PROVIDER_EXECUTOR


# ============================================================
# ENUMS
# ============================================================

class AuthenticationType(str, Enum):
    NONE = "none"
    BEARER = "bearer"
    API_KEY_HEADER = "api_key_header"
    API_KEY_QUERY = "api_key_query"
    CUSTOM = "custom"


class ProviderProtocol(str, Enum):
    REST = "rest"
    OPENAI_COMPATIBLE = "openai_compatible"
    CUSTOM = "custom"


# ============================================================
# REQUEST / RESPONSE
# ============================================================

@dataclass(slots=True)
class PromptRequest:

    prompt: str

    system_prompt: Optional[str] = None

    temperature: float = 0.7

    max_tokens: Optional[int] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderResponse:

    success: bool

    provider: str

    output: str

    raw_response: Optional[Any] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# AUTHENTICATION
# ============================================================

@dataclass(slots=True)
class AuthenticationConfig:

    type: AuthenticationType = AuthenticationType.BEARER

    token: Optional[str] = None

    header_name: str = "Authorization"

    query_name: str = "key"

    prefix: str = "Bearer"

    custom_headers: Dict[str, str] = field(default_factory=dict)


# ============================================================
# PAYLOAD MAPPING
# ============================================================

@dataclass(slots=True)
class PayloadMapping:

    prompt_field: str = "prompt"

    system_field: Optional[str] = None

    temperature_field: Optional[str] = "temperature"

    max_tokens_field: Optional[str] = "max_tokens"

    metadata_field: Optional[str] = None

    fixed_fields: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# RESPONSE MAPPING
# ============================================================

@dataclass(slots=True)
class ResponseMapping:

    output_path: Sequence[str] = field(default_factory=lambda: ("output",))


# ============================================================
# PROVIDER CONFIGURATION
# ============================================================

@dataclass(slots=True)
class ProviderConfiguration:

    name: str

    endpoint: str

    protocol: ProviderProtocol = ProviderProtocol.REST

    enabled: bool = True

    timeout_seconds: int = 60

    authentication: AuthenticationConfig = field(
        default_factory=AuthenticationConfig
    )

    payload: PayloadMapping = field(
        default_factory=PayloadMapping
    )

    response: ResponseMapping = field(
        default_factory=ResponseMapping
    )

    default_headers: Dict[str, str] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# ADAPTER CONTRACT
# ============================================================

class ProviderAdapter(ABC):

    def __init__(
        self,
        configuration: ProviderConfiguration,
    ):

        self.configuration = configuration

    @property
    def session(self):
        return HTTP_CLIENT.session()

    @property
    def executor(self):
        return PROVIDER_EXECUTOR

    @property
    def provider_name(self) -> str:
        return self.configuration.name

    @abstractmethod
    def build_headers(self) -> Dict[str, str]:
        ...

    @abstractmethod
    def build_payload(
        self,
        request: PromptRequest,
    ) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def invoke(
        self,
        request: PromptRequest,
    ) -> ProviderResponse:
        ...


# ============================================================
# BASE IMPLEMENTATION
# ============================================================

class BaseRESTAdapter(ProviderAdapter):

    def build_headers(self) -> Dict[str, str]:

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        headers.update(
            self.configuration.default_headers
        )

        auth = self.configuration.authentication

        if auth.type == AuthenticationType.BEARER:
            if auth.token:
                headers[
                    auth.header_name
                ] = f"{auth.prefix} {auth.token}"

        elif auth.type == AuthenticationType.API_KEY_HEADER:
            if auth.token:
                headers[
                    auth.header_name
                ] = auth.token

        headers.update(auth.custom_headers)

        return headers

    def build_payload(
        self,
        request: PromptRequest,
    ) -> Dict[str, Any]:

        mapping = self.configuration.payload

        payload: Dict[str, Any] = {}

        payload.update(mapping.fixed_fields)

        payload[mapping.prompt_field] = request.prompt

        if (
            mapping.system_field
            and request.system_prompt
        ):
            payload[
                mapping.system_field
            ] = request.system_prompt

        if mapping.temperature_field:
            payload[
                mapping.temperature_field
            ] = request.temperature

        if (
            mapping.max_tokens_field
            and request.max_tokens
        ):
            payload[
                mapping.max_tokens_field
            ] = request.max_tokens

        if (
            mapping.metadata_field
            and request.metadata
        ):
            payload[
                mapping.metadata_field
            ] = request.metadata

        return payload

    async def invoke(
        self,
        request: PromptRequest,
    ) -> ProviderResponse:
        raise NotImplementedError(
            "Concrete adapters implement invoke()."
        )


# ============================================================
# REGISTRY
# ============================================================

class ProviderRegistry:

    def __init__(self):

        self._configs: Dict[
            str,
            ProviderConfiguration,
        ] = {}

        self._adapters: Dict[
            str,
            type[ProviderAdapter],
        ] = {}

    def register(
        self,
        configuration: ProviderConfiguration,
        adapter: type[ProviderAdapter],
    ) -> None:

        self._configs[
            configuration.name
        ] = configuration

        self._adapters[
            configuration.name
        ] = adapter

    def unregister(
        self,
        provider: str,
    ) -> None:

        self._configs.pop(provider, None)
        self._adapters.pop(provider, None)

    def exists(
        self,
        provider: str,
    ) -> bool:

        return provider in self._configs

    def configuration(
        self,
        provider: str,
    ) -> ProviderConfiguration:

        return self._configs[provider]

    def create(
        self,
        provider: str,
    ) -> ProviderAdapter:

        configuration = self._configs[provider]

        adapter_cls = self._adapters[provider]

        return adapter_cls(configuration)

    def providers(self) -> Mapping[
        str,
        ProviderConfiguration,
    ]:

        return dict(self._configs)


PROVIDER_REGISTRY = ProviderRegistry()
