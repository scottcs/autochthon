"""AI Action Processor."""
from typing import Any

import esper

from game.component.position import Position
from game.component.playercontrolled import PlayerControlled
from game.component.solid import Solid
from game.component.velocity import Velocity
from game.component.want_to_move import WantToMove
from game.types import Entity


class AIActionProcessor(esper.Processor):
    """AI Action processor.

    This is basically just a validation step. Actual effects of the actions will
    happen in later processes.
    """
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process Collision-related components."""
        for ent, components in self.world.get_components(Position, Velocity, Solid):
            # Ignore player entities (these are handled in PlayerActionProcessor)
            if self.world.has_component(ent, PlayerControlled):
                continue

            position, velocity = components[:2]
            self.resolve_move(ent, position, velocity)
            # TODO: resolve other kinds of collisions (WantToAttack, etc)

    def resolve_move(self, entity: Entity, position: Position, velocity: Velocity) -> None:
        """Resolve any WantToMove collisions."""
        if self.world.has_component(entity, WantToMove):
            new_position = (position.x + velocity.x, position.y + velocity.y)
            found = self.world.occupied.get(new_position, None)
            if found:
                self.world.remove_component(entity, WantToMove)
                self.world.remove_component(entity, Velocity)
            else:
                self.world.occupied[(position.x, position.y)] = None
                self.world.occupied[new_position] = entity
