"""Time processor."""
import typing

import esper

import game.component.action
import game.types
import game.utils.random


class Turn(esper.Processor):
    """Turn processor."""

    queue: typing.List[game.types.Entity] = []

    def __init__(self) -> None:
        self._rng = game.utils.random.RNGCache.get("TurnProcessor")

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process turns."""
        for ent, _ in self.world.get_component(game.component.action.GUTMyTurn):
            # someone hasn't taken their turn yet
            return
        if len(self.queue) > 0:
            next_ent: game.types.Entity = self._rng.choice(self.queue)
            self.queue.remove(next_ent)
        else:
            self._reduce_initiatives()
            try:
                next_ent = self.queue.pop()
            except IndexError:
                return
        self._give_turn(next_ent)

    def _reduce_initiatives(self) -> None:
        for ent, actor in self.world.get_component(game.component.action.Actor):
            actor.initiative -= 1
            if actor.initiative <= 0:
                self.queue.append(ent)
                self._reset_actor(actor)

    def _reset_actor(self, actor: game.component.action.Actor) -> None:
        # TODO: get and apply initiative modifiers
        actor.initiative = actor.base_initiative + self._rng.rand(-2, 2)

    def _give_turn(self, ent: game.types.Entity) -> None:
        self.world.add_component(ent, game.component.action.GUTMyTurn())
