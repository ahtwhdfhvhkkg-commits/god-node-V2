"""
simulation_scheduler/frame.py

Basic simulation frame lifecycle management.
"""

from __future__ import annotations

import time
from typing import Optional

from .config import FrameConfig
from .exceptions import FrameExpired
from .types import FrameContext


class FrameManager:
    """
    Creates and manages simulation frames.

    Each call to `begin_frame()` produces a new FrameContext with a
    monotonically increasing frame identifier.
    """

    __slots__ = (
        "_config",
        "_current_frame_id",
    )

    def __init__(self, config: FrameConfig):
        self._config = config
        self._current_frame_id = 0

    @property
    def current_frame_id(self) -> int:
        """Return the most recently allocated frame ID."""
        return self._current_frame_id

    @property
    def frame_duration(self) -> float:
        """Configured frame duration in seconds."""
        return self._config.frame_duration_ms / 1000.0

    def begin_frame(self) -> FrameContext:
        """
        Create and return a new simulation frame.
        """
        self._current_frame_id += 1

        return FrameContext(
            frame_id=self._current_frame_id,
            timestamp=time.monotonic(),
            delta_time=self._config.frame_duration_ms / 1000.0,
        )

    def frame_deadline(self, frame: FrameContext) -> float:
        """
        Return the deadline timestamp for a frame.
        """
      return frame.timestamp + (self._config.frame_duration_ms / 1000.0)

    def is_expired(
        self,
        frame: FrameContext,
        *,
        now: Optional[float] = None,
    ) -> bool:
        """
        Return True if the frame has exceeded its execution window.
        """
        current_time = time.monotonic() if now is None else now
        return current_time > self.frame_deadline(frame)

    def validate(
        self,
        frame: FrameContext,
        *,
        now: Optional[float] = None,
    ) -> None:
        """
        Raise FrameExpired if the frame deadline has passed.
        """
        if self.is_expired(frame, now=now):
            raise FrameExpired(
                f"Frame {frame.frame_id} exceeded its execution deadline."
      )
