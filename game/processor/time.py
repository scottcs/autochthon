"""Time processor."""
from typing import Any

import esper

from game.component.actor import Actor


class TimeProcessor(esper.Processor):
    """Time Processor."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process time."""
        for ent, actor in self.world.get_component(Actor):
            actor.time_units += actor.rate
