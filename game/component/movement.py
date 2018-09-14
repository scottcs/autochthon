"""Movement components."""
from dataclasses import dataclass

from game.component.base import BaseModifierComponent


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


class MoveCostModifier(BaseModifierComponent):
    """Movement cost modifier."""


class GUTWaiting:
    """Waiting component."""


class WaitCostModifier(BaseModifierComponent):
    """Wait cost modifier."""
