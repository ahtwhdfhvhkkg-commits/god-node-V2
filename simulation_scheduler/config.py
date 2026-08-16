from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(slots=True, frozen=True)
class FrameConfig:
    """Simulation frame configuration."""
    frame_duration_ms: int = 16
    max_pending_frames: int = 4

@dataclass(slots=True, frozen=True)
class QueueConfig:
    """
    Scheduling queue configuration.
    Property names are explicitly aligned with PriorityTaskQueue in queue.py
    to prevent AttributeError runtime failures.
    """
    critical_capacity: int = 512      
    high_priority_capacity: int = 1024         
    normal_priority_capacity: int = 2048       
    low_priority_capacity: int = 4096          

@dataclass(slots=True, frozen=True)
class BatchConfig:
    """Micro-batch execution configuration."""
    max_batch_size: int = 64
    max_batch_wait_ms: int = 2

@dataclass(slots=True, frozen=True)
class MemoryBudget:
    """Memory budget limits for high-speed simulation."""
    max_memory_mb: int = 1024
    max_cached_results: int = 4096
    max_cached_batches: int = 512

@dataclass(slots=True, frozen=True)
class SchedulerConfig:
    """Top-level scheduler configuration."""
    frame: FrameConfig = field(default_factory=FrameConfig)
    queue: QueueConfig = field(default_factory=QueueConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)
    memory: MemoryBudget = field(default_factory=MemoryBudget)
    
    worker_count: int = 8
    enable_inference_cache: bool = True
    cache_ttl_seconds: int = 5
