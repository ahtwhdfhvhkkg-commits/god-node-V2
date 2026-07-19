"""
simulation_scheduler/queue.py

Priority queue implementation optimized for simulation scheduling.

Design goals:
- O(1) enqueue/dequeue within each priority level.
- Separate queues per priority to avoid heap overhead.
- Minimal allocations.
- Predictable iteration order.
"""

from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Iterator, Optional

from .config import QueueConfig
from .exceptions import QueueOverflow
from .priorities import SimulationPriority
from .types import SimulationTask


class PriorityTaskQueue:
    """
    Multi-level priority queue for SimulationTask objects.

    Priority order:
        CRITICAL -> HIGH -> NORMAL -> LOW

    Each priority has an independent bounded deque.
    """

    __slots__ = (
        "_queues",
        "_capacities",
        "_size",
    )

    def __init__(self, config: QueueConfig) -> None:
        self._queues: Dict[
            SimulationPriority,
            Deque[SimulationTask],
        ] = {
            priority: deque()
            for priority in SimulationPriority
        }

        self._capacities = {
            SimulationPriority.CRITICAL: config.critical_capacity,
            SimulationPriority.HIGH: config.high_capacity,
            SimulationPriority.NORMAL: config.normal_capacity,
            SimulationPriority.LOW: config.low_capacity,
        }

        self._size = 0

    # ------------------------------------------------------------------
    # Basic Properties
    # ------------------------------------------------------------------

    @property
    def size(self) -> int:
        """Total number of queued tasks."""
        return self._size

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def is_empty(self) -> bool:
        return self._size == 0

    # ------------------------------------------------------------------
    # Queue Operations
    # ------------------------------------------------------------------

    def put(self, task: SimulationTask) -> None:
        """
        Insert a task into its corresponding priority queue.
        """
        queue = self._queues[task.priority]

        if len(queue) >= self._capacities[task.priority]:
            raise QueueOverflow(
                f"{task.priority.name} queue capacity exceeded."
            )

        queue.append(task)
        self._size += 1

    def get(self) -> Optional[SimulationTask]:
        """
        Pop the next available task according to priority.
        """
        for priority in (
            SimulationPriority.CRITICAL,
            SimulationPriority.HIGH,
            SimulationPriority.NORMAL,
            SimulationPriority.LOW,
        ):
            queue = self._queues[priority]

            if queue:
                self._size -= 1
                return queue.popleft()

        return None

    def peek(self) -> Optional[SimulationTask]:
        """
        Return the next task without removing it.
        """
        for priority in (
            SimulationPriority.CRITICAL,
            SimulationPriority.HIGH,
            SimulationPriority.NORMAL,
            SimulationPriority.LOW,
        ):
            queue = self._queues[priority]

            if queue:
                return queue[0]

        return None

    def clear(self) -> None:
        """Remove all queued tasks."""
        for queue in self._queues.values():
            queue.clear()

        self._size = 0

    # ------------------------------------------------------------------
    # Batch Operations
    # ------------------------------------------------------------------

    def pop_many(self, limit: int) -> list[SimulationTask]:
        """
        Remove up to `limit` tasks while preserving priority order.
        """
        if limit <= 0 or self._size == 0:
            return []

        tasks: list[SimulationTask] = []

        while len(tasks) < limit:
            task = self.get()
            if task is None:
                break
            tasks.append(task)

        return tasks

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def queued(self, priority: SimulationPriority) -> int:
        """Return the number of tasks for a priority."""
        return len(self._queues[priority])

    def snapshot(self) -> Dict[SimulationPriority, int]:
        """Return queue sizes by priority."""
        return {
            priority: len(queue)
            for priority, queue in self._queues.items()
        }

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def __iter__(self) -> Iterator[SimulationTask]:
        """
        Iterate over tasks in scheduling order without modifying queues.
        """
        for priority in (
            SimulationPriority.CRITICAL,
            SimulationPriority.HIGH,
            SimulationPriority.NORMAL,
            SimulationPriority.LOW,
        ):
            yield from self._queues[priority]
