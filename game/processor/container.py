"""Container processor."""
import logging
from typing import Any, Optional

import esper

from game.component.container import Container, Containable, GUTContained, GUTContainerTransfer
from game.component.descriptive import Name
from game.component.gamelog import GUTCommandLog
from game.component.movement import Position
from game.events import RefreshMapEvent
from game.types import EquipType, Entity
from gamedata.palette import ItemPalette

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ContainerProcessor(esper.Processor):
    """Process containers."""

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process container components."""

        # TODO: process unequip

        # TODO: process equip

        # process all container transfers
        for containable_ent, components in self.world.get_components(
            GUTContainerTransfer, Containable, Name
        ):
            transfer, containable, name = components
            self.world.remove_component(containable_ent, GUTContainerTransfer)
            cmd_log = self.world.get_or_add_component(containable_ent, GUTCommandLog)
            contained = self.world.optional_component_for_entity(containable_ent, GUTContained)

            if transfer.to_ent is None:
                container = None
                free_slot = None
            else:
                container = self.world.component_for_entity(transfer.to_ent, Container)
                free_slot = self._get_next_free_slot(transfer.to_ent, container)
                if free_slot is None:
                    cmd_log.add(f"{container.name} is full.")
                    continue
                if not self._container_can_take(container, containable):
                    cmd_log.add(f"{container.name} can't hold that.")
                    continue

            # remove from wherever it is
            if contained:
                self.world.remove_component(containable_ent, GUTContained)
            else:
                position = self.world.optional_component_for_entity(containable_ent, Position)
                container_ent_name = self.world.optional_component_for_entity(
                    transfer.to_ent, Name
                )
                if position:
                    # it's on the ground, so something is picking it up
                    self.world.remove_component(containable_ent, Position)
                    if container_ent_name:
                        if transfer.to_ent in self.world.players:
                            cmd_log.add("You pick up ")
                        else:
                            cmd_log.add(f"{container_ent_name.generic} picks up ")
                        # TODO: colorize the item by rarity?
                        cmd_log.append(f"{name.generic}", color=ItemPalette.epic)
                        cmd_log.append(f".")
                    RefreshMapEvent.fire()
                else:
                    # TODO: what to do if can't pick up?
                    log.error(f"{containable} has no Position!")

            # put it somewhere
            if transfer.to_ent is None:
                position = self.world.optional_component_for_entity(contained.by_ent, Position)
                contained_ent_name = self.world.optional_component_for_entity(
                    contained.by_ent, Name
                )
                if position:
                    self.world.add_component(containable_ent, Position(position.x, position.y))
                    if contained_ent_name:
                        if contained.by_ent in self.world.players:
                            cmd_log.add("You drop ")
                        else:
                            cmd_log.add(f"{contained_ent_name.generic} drops ")
                        # TODO: colorize the item by rarity?
                        cmd_log.append(f"{name.generic}", color=ItemPalette.epic)
                        cmd_log.append(".")
                    RefreshMapEvent.fire()
                else:
                    # TODO: what to do if can't drop?
                    log.error(f"{contained} has no Position!")
            else:
                container_name = container and container.name or "Unknown Container"
                if free_slot is None:
                    log.error(f"{container_name} should not be full!")
                else:
                    self.world.add_component(
                        containable_ent, GUTContained(transfer.to_ent, Container, free_slot)
                    )
                    # TODO: colorize the item by rarity?
                    cmd_log.add(f"{name.generic}", color=ItemPalette.epic)
                    cmd_log.append(f" is put into {container_name}.")

    def _get_next_free_slot(self, ent: Entity, container: Container) -> Optional[int]:
        seen_slots = set()
        for _, other_contained in self.world.get_component(GUTContained):
            if other_contained.by_ent == ent and other_contained.component_class == Container:
                seen_slots.add(other_contained.slot)
        if len(seen_slots) < container.max_slots:
            for slot in range(container.max_slots):
                if slot not in seen_slots:
                    return slot
        return None

    @staticmethod
    def _container_can_take(container: Container, containable: Containable) -> bool:
        return container.equip_type != EquipType.none and (
            container.equip_type == EquipType.any
            or container.equip_type == containable.equip_type
            or containable.equip_type == EquipType.any
        )
