"""Movement processor."""
from typing import Any

import esper

from game.component.action import Actor
from game.component.ai import Enemy
from game.component.base import accumulate_modifiers
from game.component.descriptive import Name
from game.component.player import Player
from game.component.gamelog import GUTDescriptionLog
from game.component.status import GUTDead
from game.component.movement import (
    GUTMoving,
    GUTWaiting,
    Position,
    MoveCostModifier,
    WaitCostModifier,
)
from game.types import Entity
from gamedata.base_engine_values import WAIT_COST, MOVE_COST
from gamedata.palette import ItemPalette


class MovementProcessor(esper.Processor):
    """Movement processor."""

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process movement components."""
        for ent, components in self.world.get_components(Actor, GUTWaiting):
            if self.world.has_component(ent, GUTDead):
                continue
            actor = components[0]
            self.world.remove_component(ent, GUTWaiting)
            actor.time_units -= self.get_wait_action_cost(ent)

        for ent, components in self.world.get_components(Position, Actor, GUTMoving):
            if self.world.has_component(ent, GUTDead):
                continue
            position, actor, moving = components
            cell = self.world.map[moving.x, moving.y]
            if not (cell.contains_enemy or cell.contains_player) and cell.walkable:
                if self.world.optional_component_for_entity(ent, Player):
                    self.world.map.contains_player[position.y, position.x] = False
                    self.world.map.contains_player[moving.y, moving.x] = True
                elif self.world.optional_component_for_entity(ent, Enemy):
                    self.world.map.contains_enemy[position.y, position.x] = False
                    self.world.map.contains_enemy[moving.y, moving.x] = True
                position.x = moving.x
                position.y = moving.y
                actor.time_units -= self.get_move_action_cost(ent)
                if ent in self.world.players:
                    item = self.world.get_item_at_position(moving.x, moving.y)
                    if item:
                        name = self.world.optional_component_for_entity(item, Name)
                        if name:
                            desc_log = self.world.get_or_add_component(ent, GUTDescriptionLog)
                            desc_log.add(f"{name.generic}", ItemPalette.epic)
                            desc_log.append(" is here.")
            self.world.remove_component(ent, GUTMoving)

    def get_wait_action_cost(self, ent: Entity) -> int:
        """Get wait action cost."""
        mods = []
        for mod in self.world.try_component(ent, WaitCostModifier):
            mods.append(mod)
        # TODO: Calculate any other waiting cost modifiers
        modifier = accumulate_modifiers(*mods)
        return int((WAIT_COST + modifier.addend) * (1 + modifier.factor))

    def get_move_action_cost(self, ent: Entity) -> int:
        """Get move action cost."""
        mods = []
        for mod in self.world.try_component(ent, MoveCostModifier):
            mods.append(mod)
        # TODO: Calculate any other moving cost modifiers
        modifier = accumulate_modifiers(*mods)
        return int((MOVE_COST + modifier.addend) * (1 + modifier.factor))
