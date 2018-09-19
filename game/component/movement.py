"""Movement components."""
from dataclasses import dataclass


@dataclass
class Position:
    """Position component."""

    x: int = 0
    y: int = 0


@dataclass
class GUTMoving:
    """Entity wants to move to destination position."""

    x: int
    y: int


class GUTWaiting:
    """Waiting component."""
