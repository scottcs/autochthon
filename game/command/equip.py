"""Equip/Unequip command."""
from .base import BaseCommand
from game.component.container import Equipment, GUTContained, Containable
from game.component.descriptive import Name
from game.component.player import Player
from game.component.gamelog import GUTCommandLog
from game.events import (
    ChoiceAcceptedEvent,
    ChoiceDeclinedEvent,
    ChoiceFromListEvent,
    ChooseFromListEvent,
    MenuClosedEvent,
)
from game.types import EventType, EquipType
from gamedata.palette import ItemPalette


class EquipCommand(BaseCommand):
    """Equip/Unequip command."""

    def _command(self) -> None:
        for ent, _ in self.world.get_component(Player):
            items_carried = self._get_items_carried(ent)
            if items_carried:
                ChoiceFromListEvent.handle(self._on_choice)
                MenuClosedEvent.handle(self._on_menu_closed)
                ChooseFromListEvent.fire(
                    {
                        "header": "Equip/Unequip what?",
                        "items": items_carried,
                        "disable": [EquipType.none.name],
                    }
                )
            else:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add("You have nothing to eqiup!")

    def _on_choice(self, event: EventType) -> None:
        input_key = self._keys_from_event(event)
        for ent, _ in self.world.get_component(Player):
            equipment = self.world.component_for_entity(ent, Equipment)
            want_to_equip = None
            for item_ent, components in self.world.get_components(GUTContained, Name, Containable):
                contained, name, containable = components
                if contained.by_ent == ent and contained.label == input_key.key:
                    if containable.equip_type != EquipType.none and equipment:
                        want_to_equip = (containable, name)
                        break
            if want_to_equip:
                equip_count = 0
                for item_ent, components in self.world.get_components(GUTContained, Containable):
                    contained, containable = components
                    if (
                            containable.equipped
                            and containable.equip_type == want_to_equip[0].equip_type
                    ):
                        equip_count += 1
                equipment_slot = equipment.slots[want_to_equip[0].equip_type]
                name = equipment_slot["name"]
                if want_to_equip[0].equipped:
                    want_to_equip[0].equipped = False
                    cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                    cmd_log.add("You unequip ")
                    cmd_log.append(want_to_equip[1].generic, ItemPalette.epic)
                    cmd_log.append(f" from your {name} slot.")
                    ChoiceAcceptedEvent.fire()
                else:
                    if equipment_slot["max"] > equip_count:
                        want_to_equip[0].equipped = True
                        cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                        cmd_log.add("You equip ")
                        cmd_log.append(want_to_equip[1].generic, ItemPalette.epic)
                        cmd_log.append(f" in your {name} slot.")
                        ChoiceAcceptedEvent.fire()
                    else:
                        msg = f"You can't equip any more items in your {name} slot."
                        cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                        cmd_log.add(msg)
                        ChoiceDeclinedEvent.fire({"status": msg})
            else:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add("You can't find the item you want to equip.")
