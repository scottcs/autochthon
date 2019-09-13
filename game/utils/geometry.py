"""Geometry utility classes."""
from __future__ import annotations

import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class Point:
    """Represents a point."""

    x: int
    y: int


class Rect:
    """Represents a rectangle."""

    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.x1 = x
        self.y1 = y
        self.x2 = x + (w - 1)
        self.y2 = y + (h - 1)
        self.w = w
        self.h = h

    def __repr__(self) -> str:
        return f"Rect<{self.p1}, {self.p2}>"

    def __eq__(self, other: typing.Any) -> bool:
        try:
            return bool(self.p1 == other.p1 and self.p2 == other.p2)
        except AttributeError:
            return False

    def __hash__(self) -> int:
        return hash(repr(self))

    @property
    def p1(self) -> Point:
        """Top left point."""
        return Point(self.x1, self.y1)

    @property
    def p2(self) -> Point:
        """Bottom right point."""
        return Point(self.x2, self.y2)

    @property
    def center(self) -> Point:
        """Calculate the center point."""
        center_x: int = (self.x1 + self.x2) // 2
        center_y: int = (self.y1 + self.y2) // 2
        return Point(center_x, center_y)

    def intersects(self, other: Rect) -> bool:
        """Check whether this rectangle intersects with another one."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )
