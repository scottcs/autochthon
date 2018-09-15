"""Time processor."""
from typing import Any

import esper

from game.component.action import Actor, MyTurn
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
            player_time = max(actor.time_units, player_time)
        return player_time < 0


class TurnProcessor(esper.Processor):
    """Turn processor."""

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process turns."""
        to_sort = []
        for ent, _ in self.world.get_component(MyTurn):
            self.world.remove_component(ent, MyTurn)
        for ent, actor in self.world.get_component(Actor):
            to_sort.append((actor.time_units, ent))
        sorted_ents = sorted(to_sort, reverse=True)
        print(f"Sorted ents: {sorted_ents}")
        who_gets_turn = sorted_ents[0][1]
        print(f"who gets turn? {who_gets_turn}")
        self.world.add_component(who_gets_turn, MyTurn)
