"""Waiting component."""
from typing import Union

from game.utils.time import GameTime


class Waiting:
    """Waiting component."""
    def __init__(self, wait_time: Union[GameTime, int]=100) -> None:
        self.wait_time: GameTime = GameTime(wait_time)
