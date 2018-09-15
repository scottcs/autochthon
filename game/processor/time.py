"""Time processor."""
from typing import Any, List, Optional

import esper

from game.component.action import Actor, GUTMyTurn
from game.component.player import Player
from game.types import Entity


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
            player_time = max(actor.time_units, player_time)
        return player_time < 0


class TurnProcessor(esper.Processor):
    """Turn processor."""

    queue: List[Entity] = []

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process turns."""
        for _, _ in self.world.get_component(GUTMyTurn):
            # if it's anyone's turn, don't do anything
            return
        next_ent = self._get_next()
        if next_ent is not None:
            self._give_turn(next_ent)

    def _get_next(self) -> Optional[Entity]:
        try:
            return self.queue.pop(0)
        except IndexError:
            self._populate_queue()
            try:
                return self.queue.pop(0)
            except IndexError:
                return None

    def _populate_queue(self) -> None:
        to_sort = []
        for ent, actor in self.world.get_component(Actor):
            to_sort.append((actor.time_units, ent))
        self.queue.extend([l[1] for l in sorted(to_sort, reverse=True)])

    def _give_turn(self, ent: Entity) -> None:
        self.world.add_component(ent, GUTMyTurn())
