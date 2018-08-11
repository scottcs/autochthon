"""Movement components."""
from typing import Any


class Position:
    """Position component."""
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    def __str__(self) -> str:
        return f'Position<{self.x}, {self.y}>'

    def __eq__(self, other: Any) -> bool:
        if self.x == other.x and self.y == other.y:
            return True
        return False


class Moving:
    """Entity wants to move to destination position."""
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y


class Waiting:
    """Waiting component."""
