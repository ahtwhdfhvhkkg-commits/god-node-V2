"""
simulation_scheduler/batcher.py

Micro-batch builder for simulation scheduling.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from .config import BatchConfig
from .types import Batch, FrameContext, SimulationTask


class MicroBatchBuilder:
    """
    Groups SimulationTask objects into fixed-size Batch objects.

    Batch creation is bounded by BatchConfig.max_batch_size.
    The max_batch_wait_ms configuration is retained for higher-level
    schedulers that implement time-based flushing.
    """

    __slots__ = (
        "_config",
    )

    def __init__(self, config: BatchConfig) -> None:
        self._config = config

    @property
    def max_batch_size(self) -> int:
        return self._config.max_batch_size

    @property
    def max_batch_wait_ms(self) -> int:
        return self._config.max_batch_wait_ms

    def build(
        self,
        tasks: Iterable[SimulationTask],
        *,
        frame: Optional[FrameContext] = None,
    ) -> List[Batch]:
        """
        Split tasks into one or more Batch objects.

        Parameters
        ----------
        tasks:
            Iterable of SimulationTask objects.

        frame:
            Optional FrameContext attached to every generated batch.

        Returns
        -------
        List[Batch]
            Sequential micro-batches respecting max_batch_size.
        """
        batch_size = self._config.max_batch_size
        batches: List[Batch] = []

        current_tasks: List[SimulationTask] = []
        batch_index = 0

        for task in tasks:
            current_tasks.append(task)

            if len(current_tasks) >= batch_size:
                batches.append(
                    Batch(
                        batch_id=f"batch-{batch_index}",
                        tasks=current_tasks,
                        frame=frame,
                    )
                )
                batch_index += 1
                current_tasks = []

        if current_tasks:
            batches.append(
                Batch(
                    batch_id=f"batch-{batch_index}",
                    tasks=current_tasks,
                    frame=frame,
                )
            )

        return batches

    def build_single(
        self,
        tasks: Iterable[SimulationTask],
        *,
        frame: Optional[FrameContext] = None,
    ) -> Batch:
        """
        Build a single batch.

        Raises ValueError if the number of tasks exceeds max_batch_size.
        """
        task_list = list(tasks)

        if len(task_list) > self._config.max_batch_size:
            raise ValueError(
                f"Batch contains {len(task_list)} tasks "
                f"(maximum {self._config.max_batch_size})."
            )

        return Batch(
            batch_id="batch-0",
            tasks=task_list,
            frame=frame,
  )
