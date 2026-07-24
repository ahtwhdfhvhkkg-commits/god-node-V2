"""
simulation_scheduler/scheduler.py

Central orchestration layer for the simulation scheduler.

Responsibilities
----------------
- Accept SimulationTask objects.
- Deduplicate tasks using the SemanticCache.
- Queue tasks by priority.
- Manage simulation frames.
- Build micro-batches for execution.

Execution of batches is intentionally left to executor.py.
"""

from __future__ import annotations

from typing import Callable, Hashable, List, Optional

from .batcher import MicroBatchBuilder
from .config import SchedulerConfig
from .frame import FrameManager
from .inference_cache import SemanticCache
from .queue import PriorityTaskQueue
from .types import (
    Batch,
    FrameContext,
    SimulationTask,
)


class SimulationScheduler:
    """
    Coordinates queueing, frame creation, semantic deduplication,
    and micro-batch construction.

    This class intentionally contains no execution logic.
    """

    __slots__ = (
        "_config",
        "_queue",
        "_frames",
        "_batcher",
        "_cache",
        "_current_frame",
    )

    def __init__(
        self,
        config: SchedulerConfig,
    ) -> None:
        self._config = config
        self._queue = PriorityTaskQueue(config.queue)
        self._frames = FrameManager(config.frame)
        self._batcher = MicroBatchBuilder(config.batch)
        self._cache = SemanticCache(config, config.memory)
        self._current_frame: Optional[FrameContext] = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_frame(self) -> Optional[FrameContext]:
        return self._current_frame

    @property
    def queue_size(self) -> int:
        return len(self._queue)

    @property
    def cache(self) -> SemanticCache:
        return self._cache

    # ------------------------------------------------------------------
    # Frame Lifecycle
    # ------------------------------------------------------------------

    def begin_frame(self) -> FrameContext:
        """
        Start a new simulation frame.
        """
        self._current_frame = self._frames.begin_frame()

        # Opportunistic cleanup.
        self._cache.cleanup()

        return self._current_frame

    def frame_expired(self) -> bool:
        """
        Returns True if the active frame has expired.
        """
        if self._current_frame is None:
            return False

        return self._frames.is_expired(
            self._current_frame,
        )

    # ------------------------------------------------------------------
    # Queue Management
    # ------------------------------------------------------------------

    def submit(
        self,
        task: SimulationTask,
    ) -> None:
        """
        Submit a task for future execution.
        """
        self._queue.put(task)

    def submit_many(
        self,
        tasks: List[SimulationTask],
    ) -> None:
        """
        Submit multiple tasks.
        """
        for task in tasks:
            self._queue.put(task)

    # ------------------------------------------------------------------
    # Semantic Deduplication
    # ------------------------------------------------------------------

    def submit_deduplicated(
        self,
        task: SimulationTask,
        semantic_key: Hashable,
    ) -> bool:
        """
        Submit only if no matching semantic result exists.

        Returns
        -------
        bool
            True if the task was queued.
            False if it was skipped due to cache.
        """
        if self._cache.contains(semantic_key):
            return False

        self._queue.put(task)
        return True

    def remember_result(
        self,
        semantic_key: Hashable,
        result: object,
    ) -> None:
        """
        Store an execution result for future deduplication.
        """
        self._cache.put(
            semantic_key,
            result,
        )

    # ------------------------------------------------------------------
    # Batch Construction
    # ------------------------------------------------------------------

    def build_batches(self) -> List[Batch]:
        """
        Drain queued tasks into micro-batches.

        Returns
        -------
        list[Batch]
        """
        if self._current_frame is None:
            self.begin_frame()

        tasks = self._queue.pop_many(
            self.queue_size,
        )

        if not tasks:
            return []

        return self._batcher.build(
            tasks,
            frame=self._current_frame,
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Reset scheduler state.
        """
        self._queue.clear()
        self._cache.clear()
        self._current_frame = None

    def snapshot(self) -> dict[str, object]:
        """
        Return lightweight scheduler statistics.
        """
        return {
            "frame_id": (
                self._current_frame.frame_id
                if self._current_frame
                else None
            ),
            "queue_size": self.queue_size,
            "queue": self._queue.snapshot(),
            "cache": self._cache.stats(),
        }
