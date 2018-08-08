"""Collision Processor."""
from typing import Optional

import esper

from game.component.position import Position
from game.component.solid import Solid
from game.component.velocity import Velocity
from game.map import Map


class CollisionProcessor(esper.Processor):
    """Collision processor."""
    def __init__(self, game_map: Optional[Map]=None) -> None:
        super().__init__()
        self.map = game_map

    def process(self, data: dict) -> None:
        """Process Collision-related components."""
        if self.map is None:
            return
        occupied = {}
        for ent, components in self.world.get_components(Position, Solid):
            position, solid = components
            occupied[(position.x, position.y)] = ent
        for ent, components in self.world.get_components(Position, Velocity, Solid):
            position, velocity, solid = components
            new_position = (position.x + velocity.x, position.y + velocity.y)
            found = occupied.get(new_position, None)
            if found:
                self.world.remove_component(ent, Velocity)
