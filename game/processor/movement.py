"""Movement processor."""
import esper

from game.component.actor import Actor
from game.component.position import Position
from game.component.velocity import Velocity


class MovementProcessor(esper.Processor):
    """Movement processor."""
    def __init__(self) -> None:
        super().__init__()

    def process(self, data: dict) -> None:
        """Process player movement events."""
        for entity, components in self.world.get_components(Position, Velocity, Actor):
            position, velocity, actor = components
            if actor.time_units >= velocity.cost:
                position.x += velocity.x
                position.y += velocity.y
                actor.time_units -= velocity.cost
            self.world.remove_component(entity, Velocity)
