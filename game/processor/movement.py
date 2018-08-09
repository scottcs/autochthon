"""Movement processor."""
import esper

from game.component.actor import Actor
from game.component.hp import HP
from game.component.playercontrolled import PlayerControlled
from game.component.position import Position
from game.component.solid import Solid
from game.component.toggleable import Toggleable
from game.component.velocity import Velocity
from game.types import Entity


class MovementProcessor(esper.Processor):
    """Movement processor."""
    def __init__(self) -> None:
        super().__init__()

    def process(self, data: dict) -> None:
        """Process movement components."""
        # Process player first
        for entity, components in self.world.get_components(PlayerControlled,
                                                            Position, Velocity, Actor):
            data['time_passed'] = self.process_entity(entity, *components[1:])
        if data['time_passed']:
            for entity, components in self.world.get_components(Position, Velocity, Actor):
                self.process_entity(entity, *components)

    def process_entity(self,
                       entity: Entity,
                       position: Position,
                       velocity: Velocity,
                       actor: Actor) -> bool:
        """Process a single entity."""
        go_on = True
        if actor.time_units >= velocity.cost:
            new_x = position.x + velocity.x
            new_y = position.y + velocity.y
            collision = None
            for other_entity, other_components in self.world.get_components(Position, Solid):
                other_position, solid = other_components
                try:
                    hp = self.world.component_for_entity(other_entity, HP)
                except KeyError:
                    hp = None
                try:
                    toggleable = self.world.component_for_entity(other_entity, Toggleable)
                except KeyError:
                    toggleable = None
                if other_position.x == new_x and other_position.y == new_y:
                    collision = other_entity
                    if not hp and not toggleable:
                        go_on = False
            if collision is None:
                position.x = new_x
                position.y = new_y
                actor.time_units -= velocity.cost
        self.world.remove_component(entity, Velocity)
        return go_on
