"""Movement components."""
import dataclasses


@dataclasses.dataclass
class Position:
    """Position component."""

    x: int = 0
    y: int = 0


@dataclasses.dataclass
class TMPMoving:
    """Entity wants to move to destination position."""

    x: int
    y: int


class TMPWaiting:
    """Waiting component."""
