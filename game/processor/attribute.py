"""Attribute processors."""
from typing import Any

import esper

from game.component.ai import Enemy
from game.component.attribute import GUTChangeHP, HP
from game.component.descriptive import Name
from game.component.gamelog import GUTStatusLog
from game.component.movement import Position
from game.component.player import Player
from game.component.status import GUTDead
from game.utils.language import msg
from gamedata.messages.status import MsgDeath


class HPProcessor(esper.Processor):
    """HP Processor."""

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process ChangeHP."""
        for ent, components in self.world.get_components(HP, GUTChangeHP):
            hp, change = components
            hp.add_clamp(change.amount)
            if hp.value <= hp.min:
                name = self.world.get_or_add_component(ent, Name, f"Entity {ent}")
                position = self.world.optional_component_for_entity(ent, Position)
                if position:
                    if self.world.optional_component_for_entity(ent, Player):
                        self.world.map.contains_player[position.y, position.x] = False
                    elif self.world.optional_component_for_entity(ent, Enemy):
                        self.world.map.contains_enemy[position.y, position.x] = False
                log = self.world.get_or_add_component(ent, GUTStatusLog)
                log.add(*msg(self.world.players, (ent,), MsgDeath, name.specific))
                # TODO: clean up dead entities (convert to corpses? that decay?)
                self.world.kill_entity(ent)
            self.world.remove_component(ent, GUTChangeHP)
