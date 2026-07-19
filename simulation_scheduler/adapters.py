"""
simulation_scheduler/adapters.py

Dependency injection interfaces for execution and routing.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .types import Batch


@runtime_checkable
class ExecutionBackendAdapter(Protocol):
    """
    Interface for a backend capable of executing simulation batches.
    """

    def execute(self, batch: Batch) -> Any:
        """
        Execute a batch and return an implementation-defined result.
        """
        ...


@runtime_checkable
class RoutingAdapter(Protocol):
    """
    Interface for routing a batch or request to an execution provider.
    """

    def route(self, batch: Batch) -> str:
        """
        Return the identifier of the execution target for the batch.
        """
        ...
