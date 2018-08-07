"""Actor component - for storing time units of energy."""
from typing import Optional, Union

from game.utils.time import GameTime, MOMENTS_PER_TURN


class Actor:
    """Actor components use time units of energy to take actions."""
    def __init__(self, initial_units: Optional[Union[GameTime, int]]=None,
                 rate: Optional[Union[GameTime, int]]=None) -> None:
        self.time_units = GameTime(initial_units)
        self.rate = GameTime(rate or MOMENTS_PER_TURN)
