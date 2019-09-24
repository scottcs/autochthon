"""AI Processor."""
import typing

import esper

import game.component.action
import game.component.ai
import game.component.movement
import game.types
import game.utils.random


class AI(esper.Processor):
    """Artificial Intelligence processor."""

    def __init__(self) -> None:
        self._rng = game.utils.random.RNGCache.get("AIProcessor")

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process AI Components."""
        for ent, components in self.world.get_components(
            game.component.action.Actor,
            game.component.ai.DummyMind,
            game.component.action.TMPMyTurn,
        ):
            self.world.add_component(ent, game.component.movement.TMPWaiting())
        for ent, components in self.world.get_components(
            game.component.movement.Position,
            game.component.action.Actor,
            game.component.ai.SimpleMind,
            game.component.action.TMPMyTurn,
        ):
            position, actor = components[:2]
            self._try_moving(ent, position)

    def _try_moving(
        self, ent: game.types.Entity, position: game.component.movement.Position
    ) -> None:
        for _ in range(100):  # try up to 100 times
            dx = self._rng.rand(-1, 1)
            dy = self._rng.rand(-1, 1)
            while dx == 0 and dy == 0:
                dx = self._rng.rand(-1, 1)
                dy = self._rng.rand(-1, 1)
            dest = game.component.movement.Position(position.x + dx, position.y + dy)
            if (
                not self.world.map.contains_enemy[dest.y, dest.x]
                and not self.world.map.contains_player[dest.y, dest.x]
                and self.world.map.walkable[dest.y, dest.x]
            ):
                self.world.add_component(ent, game.component.movement.TMPMoving(dest.x, dest.y))
                break
