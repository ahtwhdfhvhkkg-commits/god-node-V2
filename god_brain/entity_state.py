"""
god_brain/entity_state.py

Dynamic, engine-agnostic entity state definitions.

Designed for:
- AAA game architectures
- AI-driven simulation
- Minimal memory footprint
- Serialization-friendly data structures
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class DynamicProperties:
    """
    Dynamic numerical and boolean properties.

    Numerical values are stored in `attributes`.
    Boolean or categorical state is represented by `tags`.
    """

    attributes: dict[str, float] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)


@dataclass(slots=True)
class CognitiveMemory:
    """
    Lightweight short-term cognitive memory.

    Stores entity awareness and arbitrary contextual information.
    """

    known_entities: list[str] = field(default_factory=list)
    current_threat_level: float = 0.0
    context_data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GodBrainEntity:
    """
    Master representation of an intelligent world entity.

    This structure intentionally contains only generic concepts so it
    can support any game genre or simulation domain.
    """

    entity_id: str

    properties: DynamicProperties = field(default_factory=DynamicProperties)

    memory: CognitiveMemory = field(default_factory=CognitiveMemory)

    active_intention: str = "IDLE"

    spatial_coordinates: Optional[tuple[float, float, float]] = None
