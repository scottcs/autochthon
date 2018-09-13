"""Container processor."""
from typing import Any

import esper

from game.component.container import (Container, Containable, GUTContained, GUTContainerInsert,
                                      GUTContainerRemove)
from game.component.descriptive import Name
from game.component.gamelog import GUTCommandLog
from game.component.movement import Position
from game.events import RefreshMapEvent
from game.types import EquipType
from gamedata.palette import MessagePalette, ItemPalette


class ContainerProcessor(esper.Processor):
    """Process containers."""

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process container components."""

        # TODO: process unequip

        # TODO: process equip

        # process all container removes
        for ent, components in self.world.get_components(GUTContainerRemove, GUTContained):
            remove, contained = components
            self.world.remove_component(ent, GUTContainerRemove)

        # process all container inserts
        for containable_ent, components in self.world.get_components(GUTContainerInsert,
                                                                     Containable, Name):
            insert, containable, name = components
            self.world.remove_component(containable_ent, GUTContainerInsert)
            cmd_log = self.world.get_or_add_component(containable_ent, GUTCommandLog)
            contained = self.world.optional_component_for_entity(containable_ent, GUTContained)
            container = self.world.component_for_entity(insert.container_ent, Container)
            if contained:
                insert_name = self.world.component_for_entity(insert.container_ent, Name)
                cmd_log.add(f"{name} cannot be put into {insert_name}; it is already in "
                            f"{container.name}!", MessagePalette.warning)
            else:
                if container.equip_type != EquipType.none and (
                        container.equip_type == EquipType.any
                        or container.equip_type == containable.equip_type
                        or containable.equip_type == EquipType.any
                ):
                    seen_slots = set()
                    for contained_ent, contained in self.world.get_component(GUTContained):
                        if contained.by_ent == (insert.container_ent
                                                and contained.component_class == Container):
                            seen_slots.add(contained.slot)
                    if len(seen_slots) < container.max_slots:
                        for slot in range(container.max_slots):
                            if slot not in seen_slots:
                                self.world.add_component(containable_ent, GUTContained(insert.container_ent, Container, slot))
                                if self.world.has_component(containable_ent, Position):
                                    # remove it from the world
                                    self.world.remove_component(containable_ent, Position)
                                    # TODO: colorize the item by rarity?
                                    cmd_log.add(f"{container.insert_msg} ")
                                    cmd_log.append(f"{name.generic}", color=ItemPalette.epic)
                                    cmd_log.append(f" in {container.name}.")
                                    RefreshMapEvent.fire()
                                break
                    else:
                        cmd_log.add(f"{container.name} is full.")
                else:
                    cmd_log.add(f"{container.name} can't hold that.")
