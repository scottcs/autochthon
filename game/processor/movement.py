"""Movement processor."""
from typing import Any

import esper

from game.component.actor import Actor
from game.component.position import Position
from game.component.velocity import Velocity
from game.component.want_to_move import WantToMove


class MovementProcessor(esper.Processor):
    """Movement processor."""
    def __init__(self) -> None:
        super().__init__()

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process movement components."""
        for entity, components in self.world.get_components(Position, Velocity, Actor, WantToMove):
            position, velocity, actor = components[:3]
            if actor.time_units >= velocity.cost:
                position.x += velocity.x
                position.y += velocity.y
                actor.time_units -= velocity.cost
            self.world.remove_component(entity, Velocity)
            self.world.remove_component(entity, WantToMove)
