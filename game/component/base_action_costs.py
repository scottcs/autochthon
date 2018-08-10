"""Base action costs component."""
from typing import Union

from game.utils.time import GameTime, MOMENTS_PER_TURN


class BaseActionCosts:
    """Base action costs for entities that take actions."""
    def __init__(self,
                 waiting: Union[GameTime, int]=MOMENTS_PER_TURN,
                 moving: Union[GameTime, int]=MOMENTS_PER_TURN,
                 attacking: Union[GameTime, int]=MOMENTS_PER_TURN) -> None:
        self.waiting: GameTime = GameTime(waiting)
        self.moving: GameTime = GameTime(moving)
        self.attacking: GameTime = GameTime(attacking)
