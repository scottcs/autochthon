"""Movement processor."""
from typing import Any

import esper

from game.component.action import Actor, GUTMyTurn
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
from game.events import RequestRenderEvent
from game.types import Entity
from gamedata.base_engine_values import WAIT_COST, MOVE_COST
from gamedata.palette import ItemPalette


class MovementProcessor(esper.Processor):
    """Movement processor."""

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process movement components."""
        for ent, components in self.world.get_components(Actor, GUTWaiting, GUTMyTurn):
            if self.world.has_component(ent, GUTDead):
                continue
            self.world.actor_take_action(
                ent, components[0], self.get_wait_action_cost(ent), GUTWaiting
            )

        for ent, components in self.world.get_components(Position, Actor, GUTMoving, GUTMyTurn):
            if self.world.has_component(ent, GUTDead):
                continue
            position, actor, moving = components[:3]
            cost = 0
            if (
                not (
                    self.world.map.contains_enemy[moving.y, moving.x]
                    or self.world.map.contains_player[moving.y, moving.x]
                )
                and self.world.map.walkable[moving.y, moving.x]
            ):
                if self.world.optional_component_for_entity(ent, Player):
                    self.world.map.contains_player[position.y, position.x] = False
                    self.world.map.contains_player[moving.y, moving.x] = True
                elif self.world.optional_component_for_entity(ent, Enemy):
                    self.world.map.contains_enemy[position.y, position.x] = False
                    self.world.map.contains_enemy[moving.y, moving.x] = True
                position.x = moving.x
                position.y = moving.y
                cost = self.get_move_action_cost(ent)
                if ent in self.world.players:
                    item = self.world.get_item_at_position(moving.x, moving.y)
                    if item:
                        name = self.world.optional_component_for_entity(item, Name)
                        if name:
                            desc_log = self.world.get_or_add_component(ent, GUTDescriptionLog)
                            desc_log.add(f"{name.generic}", ItemPalette.epic)
                            desc_log.append(" is here.")
            self.world.actor_take_action(ent, actor, cost, GUTMoving)
            RequestRenderEvent.fire()

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
