"""
simulation_scheduler/types.py

Core data structures for the simulation scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .priorities import SimulationPriority


@dataclass(slots=True)
class SimulationTask:
    """
    Represents a single unit of work to be scheduled.
    """

    task_id: str
    payload: Any
    priority: SimulationPriority = SimulationPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SimulationResult:
    """
    Represents the result of a completed simulation task.
    """

    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass(slots=True)
class FrameContext:
    """
    Represents a simulation frame.
    """

    frame_id: int
    timestamp: float
    delta_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Batch:
    """
    Represents a group of tasks scheduled for execution together.
    """

    batch_id: str
    tasks: List[SimulationTask] = field(default_factory=list)
    frame: Optional[FrameContext] = None

    @property
    def size(self) -> int:
        """Return the number of tasks in the batch."""
        return len(self.tasks)
