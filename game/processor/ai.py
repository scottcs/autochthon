"""AI Processor."""
import random
from typing import Any

import esper

from game.component.actor import Actor
from game.component.ai_simplemind import AISimpleMind
from game.component.moving import Moving
from game.component.position import Position
from game.types import Entity


class AIProcessor(esper.Processor):
    """Artificial Intelligence processor."""
    def __init__(self) -> None:
        super().__init__()

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process AI Components."""
        for ent, components in self.world.get_components(Position, Actor, AISimpleMind):
            position, actor = components[:2]
            if actor.time_units < 0:
                continue
            self._try_moving(ent, position)

    def _try_moving(self, ent: Entity, position: Position) -> None:
            for _ in range(100):  # try up to 100 times
                dx = random.randint(-1, 1)
                dy = random.randint(-1, 1)
                while dx == 0 and dy == 0:
                    dx = random.randint(-1, 1)
                    dy = random.randint(-1, 1)
                dest = Position(position.x + dx, position.y + dy)
                other_entity = self.world.get_solid_entity_at_position(dest.x, dest.y)
                if other_entity is None:
                    self.world.add_component(ent, Moving(dest.x, dest.y))
                    break
