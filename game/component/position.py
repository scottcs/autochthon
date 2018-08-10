"""Position component."""
from __future__ import annotations


class Position:
    """Position component."""
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    def __str__(self) -> str:
        return f'Position<{self.x}, {self.y}>'

    def __eq__(self, other: Position) -> bool:
        return self.x == other.x and self.y == other.y
