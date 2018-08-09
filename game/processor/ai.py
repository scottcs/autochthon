"""AI Processor."""
import random
from typing import Any

import esper

from game.component.ai_simplemind import AISimpleMind
from game.component.velocity import Velocity
from game.component.want_to_move import WantToMove


class AIProcessor(esper.Processor):
    """Artificial Intelligence processor."""
    def __init__(self) -> None:
        super().__init__()

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process AI Components."""
        for ent, ai in self.world.get_component(AISimpleMind):
            dx = randint(-1, 1)
            dy = randint(-1, 1)
            while dx == 0 and dy == 0:
                dx = randint(-1, 1)
                dy = randint(-1, 1)
            # WantToMove is not redundant with Velocity... maybe want to attack instead
            self.world.add_component(ent, WantToMove())
            self.world.add_component(ent, Velocity(dx, dy, ai.move_cost))
