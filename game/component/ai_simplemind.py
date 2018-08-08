"""Simple mind for AI."""
from typing import Optional, Union

from game.utils.time import GameTime


class AISimpleMind:
    """Simple AI mind."""
    def __init__(self, move_cost: Optional[Union[GameTime, int]]=None) -> None:
        self.move_cost = move_cost or GameTime(200)
