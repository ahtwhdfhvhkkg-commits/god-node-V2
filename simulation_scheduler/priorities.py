"""
simulation_scheduler/priorities.py

Priority definitions for the simulation scheduler.
"""

from __future__ import annotations

from enum import IntEnum


class SimulationPriority(IntEnum):
    """
    Priority levels for scheduled simulation tasks.

    Lower numeric values indicate higher scheduling priority.
    """

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


def priority_key(priority: SimulationPriority) -> int:
    """
    Return a sortable key for the given priority.

    Example:
        tasks.sort(key=lambda task: priority_key(task.priority))
    """
    return int(priority)


def is_higher_priority(
    left: SimulationPriority,
    right: SimulationPriority,
) -> bool:
    """
    Return True if 'left' has a higher priority than 'right'.
    """
    return left < right
