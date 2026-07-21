"""
god_brain/decision_engine.py

Dynamic utility-based decision engine for GodBrainEntity.
"""

from __future__ import annotations

import random

from .entity_state import GodBrainEntity


class DecisionEngine:
    """
    Evaluates the current state of an entity and determines its
    next high-level intention.

    The decision logic is intentionally generic and engine-agnostic,
    allowing future utility evaluators, behavior trees, GOAP, or
    planners to be layered on top.
    """

    __slots__ = ()

    _THREAT_THRESHOLD = 75.0

    def evaluate_and_decide(
        self,
        entity: GodBrainEntity,
    ) -> str:
        """
        Evaluate an entity and update its active intention.

        Decision priority:
            1. Terminal state (dead / incapacitated)
            2. High-threat response
            3. Context-driven directives
            4. Idle
        """
        properties = entity.properties
        memory = entity.memory

        tags = properties.tags
        attributes = properties.attributes
        context = memory.context_data

        # --------------------------------------------------
        # Terminal States
        # --------------------------------------------------

        if "is_dead" in tags:
            entity.active_intention = "DEAD"
            return entity.active_intention

        if "unconscious" in tags:
            entity.active_intention = "INCAPACITATED"
            return entity.active_intention

        # --------------------------------------------------
        # Threat Response
        # --------------------------------------------------

        threat = memory.current_threat_level

        if threat > self._THREAT_THRESHOLD:
            courage = attributes.get("courage", 0.5)

            if courage >= 0.5:
                intention = "COMBAT"
            else:
                intention = random.choice(
                    (
                        "FLEE",
                        "COMBAT",
                    )
                )

            entity.active_intention = intention
            return intention

        # --------------------------------------------------
        # Context-Driven Behavior
        # --------------------------------------------------

        if "patrol_route" in context:
            entity.active_intention = "PATROL"
            return entity.active_intention

        # --------------------------------------------------
        # Default
        # --------------------------------------------------

        entity.active_intention = "IDLE"
        return entity.active_intention
