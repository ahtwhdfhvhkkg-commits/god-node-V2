from __future__ import annotations

from dataclasses import dataclass
from typing import Any


from .entity_state import GodBrainEntity


@dataclass(slots=True, frozen=True)
class ActionPayload:
    """
    Lightweight execution payload produced by the God Brain.

    This object is intentionally engine-agnostic and can be
    serialized or adapted into a SimulationTask by the
    execution layer.
    """

    agent_id: str
    action: str
    target_coords: tuple[float, float, float] | None
    metadata: dict[str, Any]


class ActionDispatcher:
    """
    Converts high-level AI intentions into execution payloads.

    This module intentionally does not know anything about the
    simulation scheduler implementation. It simply produces
    normalized action payloads that another layer may translate
    into SimulationTask instances.
    """

    __slots__ = ()

    def dispatch(self, entity: GodBrainEntity) -> ActionPayload:
        """
        Convert an entity's current intention into an execution payload.
        """

        metadata: dict[str, Any] = {
            "attributes": dict(entity.properties.attributes),
            "tags": tuple(sorted(entity.properties.tags)),
            "context": dict(entity.memory.context_data),
            "threat_level": entity.memory.current_threat_level,
        }

        return ActionPayload(
            agent_id=entity.entity_id,
            action=entity.active_intention,
            target_coords=entity.spatial_coordinates,
            metadata=metadata,
        )

    def as_dict(self, entity: GodBrainEntity) -> dict[str, Any]:
        """
        Return the execution payload as a standard dictionary.
        """

        payload = self.dispatch(entity)

        return {
            "agent_id": payload.agent_id,
            "action": payload.action,
            "target_coords": payload.target_coords,
            "metadata": payload.metadata,
  }
