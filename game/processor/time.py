"""Time processor."""
from typing import Any, List, Optional

import esper

from game.component.action import Actor, GUTMyTurn
from game.component.status import GUTDead
from game.types import Entity
from game.utils.random import RNGCache


class TurnProcessor(esper.Processor):
    """Turn processor."""

    queue: List[Entity] = []

    def __init__(self):
        super().__init__()
        self._rng = RNGCache.get("TurnProcessor")

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process turns."""
        for ent, _ in self.world.get_component(GUTMyTurn):
            if not self.world.has_component(ent, GUTDead):
                # if it's anyone's turn (who's still alive), don't do anything
                return
        next_ent = self._get_next()
        while next_ent and self.world.optional_component_for_entity(next_ent, GUTDead):
            # skip dead actors
            next_ent = self._get_next()
        if next_ent is not None:
            self._give_turn(next_ent)
            self._populate_queue()

    def _get_next(self) -> Optional[Entity]:
        # every actor gets +1 to counter until someone has counter >= initiative
        next_ent = None
        while next_ent is None:
            to_remove: List[Entity] = []
            for ent in self.queue:
                try:
                    actor = self.world.component_for_entity(Actor)
                except KeyError:
                    to_remove.append(ent)
                    continue
                actor.counter += 1
            for ent in to_remove:
                self.queue.remove(ent)
            if len(self.queue) == 0:
                self._reset_actors()
                self._populate_queue()
            first_actor: Actor = self.world.component_for_entity(self.queue[0], Actor)
            if first_actor.counter >= first_actor.initiative:
                next_ent = self.queue.pop(0)
                self._reset_actor(first_actor)
        return next_ent

    def _reset_actor(self, actor: Actor) -> None:
        # TODO: get and apply initiative modifiers
        actor.initiative = actor.base_initiative + self._rng.rand(-2, 2)
        actor.counter = 0

    def _reset_actors(self) -> None:
        for _, actor in self.world.get_component(Actor):
            self._reset_actor(actor)

    def _populate_queue(self) -> None:
        to_sort = []
        for ent, actor in self.world.get_component(Actor):
            to_sort.append((actor.initiative, ent))
        self.queue = [l[1] for l in sorted(to_sort)]

    def _give_turn(self, ent: Entity) -> None:
        self.world.add_component(ent, GUTMyTurn())
