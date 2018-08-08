"""Velocity component."""
from typing import Union

from game.utils.time import GameTime


class Velocity:
    """Velocity component."""
    def __init__(self, x: int, y: int, cost: Union[GameTime, int]) -> None:
        self.x: int = x
        self.y: int = y
        self.cost: GameTime = GameTime(cost)
