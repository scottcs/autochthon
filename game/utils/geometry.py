"""Geometry utility classes."""
from __future__ import annotations
from typing import NamedTuple


class Point(NamedTuple):
    """Represents a point."""

    x: int
    y: int


class Rect:
    """Represents a rectangle."""

    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.p1: Point = Point(x, y)
        self.p2: Point = Point(x + w, y + h)

    def __repr__(self) -> str:
        return f'Rect<{self.p1}, {self.p2}>'

    def __hash__(self) -> int:
        return hash(repr(self))

    @property
    def center(self) -> Point:
        """Calculate the center point."""
        center_x: int = (self.p1.x + self.p2.x) // 2
        center_y: int = (self.p1.y + self.p2.y) // 2
        return Point(center_x, center_y)

    def intersects(self, other: Rect) -> bool:
        """Check whether this rectangle intersects with another one."""
        return (self.p1.x <= other.p2.x and self.p2.x >= other.p1.x and
                self.p1.y <= other.p2.y and self.p2.y >= other.p1.y)
