"""Movement processor."""
from typing import Any

import esper

from game.component.action import Actor, GUTMyTurn
from game.component.ai import Enemy
from game.component.descriptive import Name
from game.component.player import Player
from game.component.gamelog import GUTDescriptionLog
from game.component.status import GUTDead
from game.component.movement import GUTMoving, GUTWaiting, Position
from game.events import RenderEntitiesEvent, RenderMapEvent
from gamedata.palette import ItemPalette


class MovementProcessor(esper.Processor):
    """Movement processor."""

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process movement components."""
        entities_to_render: list = []
        for ent, components in self.world.get_components(Actor, GUTWaiting, GUTMyTurn):
            if self.world.has_component(ent, GUTDead):
                continue
            self.world.actor_takes_turn(ent, GUTWaiting)

        for ent, components in self.world.get_components(Position, Actor, GUTMoving, GUTMyTurn):
            if self.world.has_component(ent, GUTDead):
                continue
            position, actor, moving = components[:3]
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
                entities_to_render.append(ent)
                if ent in self.world.players:
                    RenderMapEvent.fire()
                    item = self.world.get_item_at_position(moving.x, moving.y)
                    if item:
                        name = self.world.optional_component_for_entity(item, Name)
                        if name:
                            desc_log = self.world.get_or_add_component(ent, GUTDescriptionLog)
                            desc_log.add(f"{name.generic}", ItemPalette.epic)
                            desc_log.append(" is here.")
            self.world.actor_takes_turn(ent, GUTMoving)
            if entities_to_render:
                RenderEntitiesEvent.fire({"entities": entities_to_render})
