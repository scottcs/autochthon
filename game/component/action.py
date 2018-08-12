"""Action components."""
from typing import Union

from game.utils.time import GameTime
from gamedata.base_engine_values import MOMENTS_PER_TURN


class Actor:
    """Actor components use time units of energy to take actions."""
    def __init__(self, initial_units: Union[GameTime, int]=0,
                 rate: Union[GameTime, int]=MOMENTS_PER_TURN) -> None:
        self.time_units: GameTime = GameTime(initial_units)
        self.rate: GameTime = GameTime(rate)

    def __str__(self) -> str:
        return (f'{self.time_units} ({self.time_units.last_time}/{self.time_units.last_change}) '
                f'(+{self.rate}/turn)')
