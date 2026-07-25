"""
simulation_scheduler/config.py

Configuration settings for the God Node Simulation Scheduler.
"""
from dataclasses import dataclass, field

@dataclass
class QueueConfig:
    max_size: int = 10000
    critical_capacity: int = 8000  # <--- यही वो नाम है जो इंजन ढूँढ रहा था!
    priority_levels: int = 3

@dataclass
class FrameConfig:
    max_duration_sec: float = 0.16
    target_fps: int = 60

@dataclass
class BatchConfig:
    max_batch_size: int = 500
    timeout_ms: int = 10

@dataclass
class CacheConfig:
    enabled: bool = True
    ttl_seconds: int = 60

@dataclass
class SchedulerConfig:
    queue: QueueConfig = field(default_factory=QueueConfig)
    frame: FrameConfig = field(default_factory=FrameConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)
    memory: CacheConfig = field(default_factory=CacheConfig)
