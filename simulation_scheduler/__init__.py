"""
simulation_scheduler

Public API for the simulation scheduler package.
"""

from .adapters import ExecutionBackendAdapter, RoutingAdapter
from .batcher import MicroBatchBuilder
from .config import (
    BatchConfig,
    FrameConfig,
    MemoryBudget,
    QueueConfig,
    SchedulerConfig,
)
from .executor import SimulationExecutor
from .frame import FrameManager
from .inference_cache import SemanticCache
from .priorities import SimulationPriority
from .queue import PriorityTaskQueue
from .scheduler import SimulationScheduler
from .types import (
    Batch,
    FrameContext,
    SimulationResult,
    SimulationTask,
)

__all__ = [
    # Core
    "SimulationScheduler",
    "SimulationExecutor",
    # Configuration
    "SchedulerConfig",
    "FrameConfig",
    "QueueConfig",
    "BatchConfig",
    "MemoryBudget",
    # Types
    "SimulationTask",
    "SimulationResult",
    "FrameContext",
    "Batch",
    # Priority
    "SimulationPriority",
    # Components
    "FrameManager",
    "PriorityTaskQueue",
    "MicroBatchBuilder",
    "SemanticCache",
    # Dependency Injection
    "ExecutionBackendAdapter",
    "RoutingAdapter",
]
