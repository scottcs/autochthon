"""Movement processor."""
import logging
import typing

import esper

import game.component.action
import game.component.ai
import game.component.descriptive
import game.component.gamelog
import game.component.movement
import game.component.player
import game.component.status
import game.events
import game.palette

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Movement(esper.Processor):
    """Movement processor."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process movement components."""
        entities_need_rendering = False
        for ent, components in self.world.get_components(
            game.component.action.Actor,
            game.component.movement.TMPWaiting,
            game.component.action.TMPMyTurn,
        ):
            if self.world.has_component(ent, game.component.status.TMPDead):
                continue
            self.world.actor_takes_turn(ent, game.component.movement.TMPWaiting)

        for ent, components in self.world.get_components(
            game.component.movement.Position,
            game.component.action.Actor,
            game.component.movement.TMPMoving,
            game.component.action.TMPMyTurn,
        ):
            if self.world.has_component(ent, game.component.status.TMPDead):
                continue
            position, actor, moving = components[:3]
            if (
                not (
                    self.world.map.contains_enemy[moving.y, moving.x]
                    or self.world.map.contains_player[moving.y, moving.x]
                )
                and self.world.map.walkable[moving.y, moving.x]
            ):
                if self.world.optional_component_for_entity(ent, game.component.player.Player):
                    self.world.map.contains_player[position.y, position.x] = False
                    self.world.map.contains_player[moving.y, moving.x] = True
                elif self.world.optional_component_for_entity(ent, game.component.ai.Enemy):
                    self.world.map.contains_enemy[position.y, position.x] = False
                    self.world.map.contains_enemy[moving.y, moving.x] = True
                position.x = moving.x
                position.y = moving.y
                entities_need_rendering = True
                if ent in self.world.players:
                    player = self.world.component_for_entity(ent, game.component.player.Player)
                    self.world.map.update_fov(position.x, position.y, radius=player.fov)
                    game.events.RenderMap()
                    item = self.world.get_item_at_position(moving.x, moving.y)
                    if item:
                        name = self.world.optional_component_for_entity(
                            item, game.component.descriptive.Name
                        )
                        if name:
                            desc_log = self.world.get_or_add_component(
                                ent, game.component.gamelog.TMPDescription
                            )
                            desc_log.add(f"{name.generic}", game.palette.Item.epic)
                            desc_log.add_raw(" is here.")
            self.world.actor_takes_turn(ent, game.component.movement.TMPMoving)
            if entities_need_rendering:
                game.events.RenderEntities()
