"""Movement processor."""
from typing import Any

import esper

from game.component.actor import Actor
from game.component.base_action_costs import BaseActionCosts
from game.component.moving import Moving
from game.component.position import Position
from game.component.waiting import Waiting


class MovementProcessor(esper.Processor):
    """Movement processor."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process movement components."""
        for ent, components in self.world.get_components(Actor, BaseActionCosts, Waiting):
            actor, base_costs = components[:2]
            self.world.remove_component(ent, Waiting)
            # TODO: Calculate any waiting cost modifiers
            actor.time_units -= base_costs.waiting

        for ent, components in self.world.get_components(Position, Actor, BaseActionCosts, Moving):
            position, actor, base_costs, moving = components
            other_solid = self.world.get_solid_entity_at_position(moving.x, moving.y)
            if other_solid is None and self.world.map[moving.x, moving.y].walkable:
                position.x = moving.x
                position.y = moving.y
                # TODO: Calculate any moving cost modifiers
                actor.time_units -= base_costs.moving
            self.world.remove_component(ent, Moving)
