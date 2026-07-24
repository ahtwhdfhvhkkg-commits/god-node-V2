"""
simulation_scheduler/executor.py

Execution coordinator for the simulation scheduler.
"""

from __future__ import annotations

from typing import Any, List

from .adapters import ExecutionBackendAdapter
from .scheduler import SimulationScheduler


class SimulationExecutor:
    """
    Coordinates scheduling and execution.

    The executor is intentionally lightweight. It delegates task
    scheduling to SimulationScheduler and task execution to an
    injected ExecutionBackendAdapter.
    """

    __slots__ = (
        "_scheduler",
        "_backend",
    )

    def __init__(
        self,
        scheduler: SimulationScheduler,
        backend: ExecutionBackendAdapter,
    ) -> None:
        self._scheduler = scheduler
        self._backend = backend

    @property
    def scheduler(self) -> SimulationScheduler:
        return self._scheduler

    @property
    def backend(self) -> ExecutionBackendAdapter:
        return self._backend

    def run_frame(self) -> List[Any]:
        """
        Execute all batches generated for the current simulation frame.

        Returns
        -------
        list
            A list containing the result returned by the execution
            backend for each processed batch.
        """
        batches = self._scheduler.build_batches()

        if not batches:
            return []

        results: List[Any] = []

        for batch in batches:
            results.append(
                self._backend.execute(batch)
            )

        return results

    def tick(self) -> List[Any]:
        """
        Alias for run_frame().
        """
        return self.run_frame()
