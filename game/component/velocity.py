"""Velocity component."""
from game.utils.time import GameTime


class Velocity:
    """Velocity component."""
    def __init__(self, x: int, y: int, speed: GameTime) -> None:
        self.x: int = x
        self.y: int = y
        self.speed: GameTime = speed
