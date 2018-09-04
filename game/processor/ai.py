"""AI Processor."""
from typing import Any

import esper

from game.component.action import Actor
from game.component.ai import AISimpleMind
from game.component.movement import GUTMoving, Position
from game.component.status import Solid
from game.types import Entity
from game.utils.random import RNGCache


class AIProcessor(esper.Processor):
    """Artificial Intelligence processor."""
    def __init__(self) -> None:
        super().__init__()
        self._rng = RNGCache.get('AIProcessor')

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process AI Components."""
        for ent, components in self.world.get_components(Position, Actor, AISimpleMind):
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
                other_entity = self.world.get_entity_at_position(dest.x, dest.y, Solid)
                if other_entity is None and self.world.map[dest.x, dest.y].walkable:
                    self.world.add_component(ent, GUTMoving(dest.x, dest.y))
                    break
