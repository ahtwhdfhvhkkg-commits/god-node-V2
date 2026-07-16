"""
simulation_scheduler/exceptions.py

Custom exception hierarchy for the simulation scheduler.

These exceptions provide a consistent error model for scheduling,
batching, execution, and adapter integration.
"""

from __future__ import annotations


class SchedulerError(Exception):
    """Base exception for all simulation scheduler errors."""


class QueueOverflow(SchedulerError):
    """Raised when a scheduling queue has reached its configured capacity."""


class FrameExpired(SchedulerError):
    """Raised when a simulation frame expires before execution."""


class BatchRejected(SchedulerError):
    """Raised when a batch cannot be accepted for execution."""


class ExecutionFailure(SchedulerError):
    """Raised when execution of a scheduled batch fails."""


class AdapterError(SchedulerError):
    """Raised when an external execution or routing adapter fails."""


class SchedulerNotRunning(SchedulerError):
    """Raised when work is submitted before the scheduler has started."""


class SchedulerShuttingDown(SchedulerError):
    """Raised when new work is submitted during scheduler shutdown."""


class InvalidTask(SchedulerError):
    """Raised when a submitted task is invalid or incomplete."""


class InvalidFrame(SchedulerError):
    """Raised when a frame contains invalid scheduling metadata."""


class QueueClosed(SchedulerError):
    """Raised when attempting to enqueue work into a closed queue."""


class BatchTimeout(ExecutionFailure):
    """Raised when batch execution exceeds its allotted timeout."""


class CacheError(SchedulerError):
    """Raised when an inference cache operation fails."""


class ConfigurationError(SchedulerError):
    """Raised when scheduler configuration is invalid."""
