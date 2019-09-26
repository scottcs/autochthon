"""Container processor."""
import logging
import typing

import esper

import game.component.container
import game.component.descriptive
import game.component.gamelog
import game.component.movement
import game.events
import game.palette
import game.types

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Container(esper.Processor):
    """Process containers."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process container components."""
        entities_need_rendering: bool = False

        # TODO: process unequip

        # TODO: process equip

        # process all container transfers
        for containable_ent, components in self.world.get_components(
            game.component.container.TMPTransfer,
            game.component.container.Containable,
            game.component.descriptive.Name,
        ):
            transfer, containable, name = components
            self.world.remove_component(containable_ent, game.component.container.TMPTransfer)
            cmd_log = self.world.get_or_add_component(
                containable_ent, game.component.gamelog.TMPCommand
            )
            contained = self.world.optional_component_for_entity(
                containable_ent, game.component.container.TMPContained
            )

            if transfer.to_ent is None:
                container = None
                free_slot = None
            else:
                container = self.world.component_for_entity(
                    transfer.to_ent, game.component.container.Container
                )
                free_slot = self._get_next_free_slot(transfer.to_ent, container)
                if free_slot is None:
                    cmd_log.add(f"{container.name} is full.")
                    continue
                if not self._container_can_take(container, containable):
                    cmd_log.add(f"{container.name} can't hold that.")
                    continue

            # remove from wherever it is
            if contained:
                self.world.remove_component(containable_ent, game.component.container.TMPContained)
            else:
                position = self.world.optional_component_for_entity(
                    containable_ent, game.component.movement.Position
                )
                container_ent_name = self.world.optional_component_for_entity(
                    transfer.to_ent, game.component.descriptive.Name
                )
                if position:
                    # it's on the ground, so something is picking it up
                    self.world.remove_component(containable_ent, game.component.movement.Position)
                    self.world.map.contains_item[position.y, position.x] = False
                    if container_ent_name:
                        if transfer.to_ent in self.world.players:
                            cmd_log.add("You pick up ")
                        else:
                            cmd_log.add(f"{container_ent_name.generic} picks up ")
                        # TODO: colorize the item by rarity?
                        cmd_log.add_raw(f"{name.generic}", color=game.palette.Item.epic)
                        cmd_log.add_raw(f".")
                        log.debug(f"Picked up {containable_ent}")
                    entities_need_rendering = True
                else:
                    # TODO: what to do if can't pick up?
                    log.error(f"{containable} has no Position!")

            # put it somewhere
            if transfer.to_ent is None:
                position = self.world.optional_component_for_entity(
                    contained.by_ent, game.component.movement.Position
                )
                contained_ent_name = self.world.optional_component_for_entity(
                    contained.by_ent, game.component.descriptive.Name
                )
                if position:
                    self.world.add_component(
                        containable_ent, game.component.movement.Position(position.x, position.y)
                    )
                    self.world.map.contains_item[position.y, position.x] = True
                    if contained_ent_name:
                        if contained.by_ent in self.world.players:
                            cmd_log.add("You drop ")
                        else:
                            cmd_log.add(f"{contained_ent_name.generic} drops ")
                        # TODO: colorize the item by rarity?
                        cmd_log.add_raw(f"{name.generic}", color=game.palette.Item.epic)
                        cmd_log.add_raw(".")
                    entities_need_rendering = True
                else:
                    # TODO: what to do if can't drop?
                    log.error(f"{contained} has no Position!")
            else:
                container_name = container and container.name or "Unknown Container"
                if free_slot is None:
                    log.error(f"{container_name} should not be full!")
                else:
                    self.world.add_component(
                        containable_ent,
                        game.component.container.TMPContained(
                            transfer.to_ent, game.component.container.Container, free_slot
                        ),
                    )
                    if contained:
                        # TODO: colorize the item by rarity?
                        cmd_log.add(f"{name.generic}", color=game.palette.Item.epic)
                        cmd_log.add_raw(f" is put into {container_name}.")
        if entities_need_rendering:
            game.events.RenderEntities.fire()

    def _get_next_free_slot(
        self, ent: game.types.Entity, container: game.component.container.Container
    ) -> typing.Optional[int]:
        seen_slots = set()
        for _, other_contained in self.world.get_component(game.component.container.TMPContained):
            if (
                other_contained.by_ent == ent
                and other_contained.component_class == game.component.container.Container
            ):
                seen_slots.add(other_contained.slot)
        if len(seen_slots) < container.max_slots:
            for slot in range(container.max_slots):
                if slot not in seen_slots:
                    return slot
        return None

    @staticmethod
    def _container_can_take(
        container: game.component.container.Container,
        containable: game.component.container.Containable,
    ) -> bool:
        return container.equip_type != game.types.Equip.none and (
            container.equip_type == game.types.Equip.any
            or container.equip_type == containable.equip_type
            or containable.equip_type == game.types.Equip.any
        )
