"""Collision Processor."""
import esper

from game.component.position import Position
from game.component.solid import Solid
from game.component.velocity import Velocity
from game.component.want_to_move import WantToMove
from game.types import Entity


class CollisionProcessor(esper.Processor):
    """Collision processor.

    This is basically just a validation step. Actual effects of the collision will
    happen in later processes.
    """
    def __init__(self) -> None:
        super().__init__()
        self.occupied: dict = {}

    def process(self, data: dict) -> None:
        """Process Collision-related components."""
        self.occupied.clear()
        for ent, components in self.world.get_components(Position, Solid):
            position = components[0]
            self.occupied[(position.x, position.y)] = ent
        for ent, components in self.world.get_components(Position, Velocity, Solid):
            position, velocity = components[:2]
            self.resolve_move(ent, position, velocity)
            # TODO: resolve other kinds of collisions (WantToAttack, etc)

    def resolve_move(self, entity: Entity, position: Position, velocity: Velocity):
        """Resolve any WantToMove collisions."""
        for _ in self.world.try_component(entity, WantToMove):
            new_position = (position.x + velocity.x, position.y + velocity.y)
            found = self.occupied.get(new_position, None)
            if found:
                self.world.remove_component(entity, WantToMove)
                self.world.remove_component(entity, Velocity)
            else:
                self.occupied[(position.x, position.y)] = None
                self.occupied[new_position] = entity
