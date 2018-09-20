"""Time processor."""
from typing import Any, List

import esper

from game.component.action import Actor, GUTMyTurn
from game.types import Entity
from game.utils.random import RNGCache


class TurnProcessor(esper.Processor):
    """Turn processor."""

    queue: List[Entity] = []

    def __init__(self) -> None:
        super().__init__()
        self._rng = RNGCache.get("TurnProcessor")

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process turns."""
        for ent, _ in self.world.get_component(GUTMyTurn):
            # someone hasn't taken their turn yet
            return
        if len(self.queue) > 0:
            next_ent: Entity = self._rng.choice(self.queue)
            self.queue.remove(next_ent)
        else:
            self._reduce_initiatives()
            try:
                next_ent = self.queue.pop()
            except IndexError:
                return
        self._give_turn(next_ent)

    def _reduce_initiatives(self) -> None:
        for ent, actor in self.world.get_component(Actor):
            actor.initiative -= 1
            if actor.initiative <= 0:
                self.queue.append(ent)
                self._reset_actor(actor)

    def _reset_actor(self, actor: Actor) -> None:
        # TODO: get and apply initiative modifiers
        actor.initiative = actor.base_initiative + self._rng.rand(-2, 2)

    def _give_turn(self, ent: Entity) -> None:
        self.world.add_component(ent, GUTMyTurn())
