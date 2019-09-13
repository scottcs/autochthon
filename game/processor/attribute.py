"""Attribute processors."""
import typing

import esper

import game.component.ai
import game.component.attribute
import game.component.descriptive
import game.component.gamelog
import game.component.movement
import game.component.player
import game.utils.language
import gamedata.messages.status


class HPProcessor(esper.Processor):
    """HP Processor."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process ChangeHP."""
        for ent, components in self.world.get_components(
            game.component.attribute.HP, game.component.attribute.GUTChangeHP
        ):
            hp, change = components
            hp.add_clamp(change.amount)
            if hp.value <= hp.min:
                name = self.world.get_or_add_component(
                    ent, game.component.descriptive.Name, f"Entity {ent}"
                )
                position = self.world.optional_component_for_entity(
                    ent, game.component.movement.Position
                )
                if position:
                    if self.world.optional_component_for_entity(ent, game.component.player.Player):
                        self.world.map.contains_player[position.y, position.x] = False
                    elif self.world.optional_component_for_entity(ent, game.component.ai.Enemy):
                        self.world.map.contains_enemy[position.y, position.x] = False
                log = self.world.get_or_add_component(ent, game.component.gamelog.GUTStatusLog)
                log.add(
                    *game.utils.language.msg(
                        self.world.players,
                        (ent,),
                        gamedata.messages.status.MsgDeath,
                        name.specific,
                    )
                )
                # TODO: clean up dead entities (convert to corpses? that decay?)
                self.world.kill_entity(ent)
            self.world.remove_component(ent, game.component.attribute.GUTChangeHP)
