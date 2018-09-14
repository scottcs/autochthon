"""Time processor."""
from typing import Any

import esper

from game.component.action import Actor
from game.component.player import Player


class TimeProcessor(esper.Processor):
    """Time Processor."""

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process time."""
        while self._should_tick():
            for ent, actor in self.world.get_component(Actor):
                actor.time_units += actor.rate

    def _should_tick(self) -> bool:
        player_time = -1
        for ent, components in self.world.get_components(Actor, Player):
            actor = components[0]
            player_time = max(int(actor.time_units), player_time)
        return player_time < 0
