"""Time processor."""
from typing import Any

import esper

from game.component.actor import Actor
from game.component.playercontrolled import PlayerControlled


class TimeProcessor(esper.Processor):
    """Time processor."""

    def __init__(self) -> None:
        super().__init__()

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process time."""
        if self.world.turn_time:
            for ent, actor in self.world.get_component(Actor):
                actor.time_units += self.world.turn_time
