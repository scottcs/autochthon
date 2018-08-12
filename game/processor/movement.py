"""Movement processor."""
from typing import Any

import esper

from game.component.action import Actor
from game.component.base import accumulate_modifiers
from game.component.status import Dead
from game.component.movement import Moving, Waiting, Position, MoveCostModifier, WaitCostModifier
from gamedata.base_engine_values import WAIT_COST, MOVE_COST
from game.types import Entity


class MovementProcessor(esper.Processor):
    """Movement processor."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process movement components."""
        for ent, components in self.world.get_components(Actor, Waiting):
            if self.world.has_component(ent, Dead):
                continue
            actor = components[0]
            self.world.remove_component(ent, Waiting)
            actor.time_units -= self.get_wait_action_cost(ent)

        for ent, components in self.world.get_components(Position, Actor, Moving):
            if self.world.has_component(ent, Dead):
                continue
            position, actor, moving = components
            other_solid = self.world.get_solid_entity_at_position(moving.x, moving.y)
            if other_solid is None and self.world.map[moving.x, moving.y].walkable:
                position.x = moving.x
                position.y = moving.y
                actor.time_units -= self.get_move_action_cost(ent)
            self.world.remove_component(ent, Moving)

    def get_wait_action_cost(self, ent: Entity) -> int:
        """Get wait action cost."""
        mods = []
        for mod in self.world.try_component(ent, WaitCostModifier):
            mods.append(mod)
        # TODO: Calculate any other waiting cost modifiers
        modifier = accumulate_modifiers(*mods)
        return (WAIT_COST + modifier.addend) * (1 + modifier.factor)

    def get_move_action_cost(self, ent: Entity) -> int:
        """Get move action cost."""
        mods = []
        for mod in self.world.try_component(ent, MoveCostModifier):
            mods.append(mod)
        # TODO: Calculate any other moving cost modifiers
        modifier = accumulate_modifiers(*mods)
        return (MOVE_COST + modifier.addend) * (1 + modifier.factor)
