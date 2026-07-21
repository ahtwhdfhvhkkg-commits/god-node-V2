"""
god_brain/memory_vault.py

Memory management utilities for GodBrainEntity instances.
"""

from __future__ import annotations

from typing import Any

from .entity_state import CognitiveMemory, GodBrainEntity


class MemoryVault:
    """
    Stateless manager responsible for maintaining the cognitive memory
    of GodBrainEntity instances.
    """

    __slots__ = ()

    MAX_KNOWN_ENTITIES = 50

    def register_sighting(
        self,
        entity: GodBrainEntity,
        target_id: str,
    ) -> None:
        """
        Register that an entity has observed another entity.

        Duplicate entries are ignored. The known entity list is capped
        to avoid unbounded memory growth.
        """
        known = entity.memory.known_entities

        if target_id in known:
            return

        known.append(target_id)

        if len(known) > self.MAX_KNOWN_ENTITIES:
            del known[:-self.MAX_KNOWN_ENTITIES]

    def update_threat(
        self,
        entity: GodBrainEntity,
        threat_delta: float,
    ) -> None:
        """
        Increment or decrement the current threat level.

        The threat level is always clamped to a minimum of 0.0.
        """
        memory = entity.memory

        memory.current_threat_level = max(
            0.0,
            memory.current_threat_level + threat_delta,
        )

    def store_context(
        self,
        entity: GodBrainEntity,
        key: str,
        value: Any,
    ) -> None:
        """
        Store arbitrary contextual information for the entity.
        """
        entity.memory.context_data[key] = value

    def clear_memory(
        self,
        entity: GodBrainEntity,
    ) -> None:
        """
        Reset the entity's cognitive memory to its default state.
        """
        entity.memory = CognitiveMemory()
