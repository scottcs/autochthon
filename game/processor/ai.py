"""AI Processor."""
from typing import Any

import esper

from game.component.action import Actor, GUTMyTurn
from game.component.ai import AISimpleMind, AIDummy
from game.component.movement import GUTMoving, Position, GUTWaiting
from game.types import Entity
from game.utils.random import RNGCache


class AIProcessor(esper.Processor):
    """Artificial Intelligence processor."""

    def __init__(self) -> None:
        super().__init__()
        self._rng = RNGCache.get("AIProcessor")

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process AI Components."""
        for ent, components in self.world.get_components(Actor, AIDummy, GUTMyTurn):
            actor = components[0]
            if actor.time_units < 0:
                continue
            self.world.add_component(ent, GUTWaiting())
        for ent, components in self.world.get_components(Position, Actor, AISimpleMind, GUTMyTurn):
            position, actor = components[:2]
            if actor.time_units < 0:
                continue
            self._try_moving(ent, position)

    def _try_moving(self, ent: Entity, position: Position) -> None:
        for _ in range(100):  # try up to 100 times
            dx = self._rng.rand(-1, 1)
            dy = self._rng.rand(-1, 1)
            while dx == 0 and dy == 0:
                dx = self._rng.rand(-1, 1)
                dy = self._rng.rand(-1, 1)
            dest = Position(position.x + dx, position.y + dy)
            if (not self.world.map.contains_enemy[dest.y, dest.x]
                    and not self.world.map.contains_player[dest.y, dest.x]
                    and self.world.map.walkable[dest.y, dest.x]):
                self.world.add_component(ent, GUTMoving(dest.x, dest.y))
                break
