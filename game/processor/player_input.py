"""User input processing."""
import json
import logging
from pathlib import Path
from typing import Any, Mapping

import esper

from game.component.container import Containable, GUTContained, Equipment
from game.component.descriptive import Name
from game.component.gamelog import GUTCommandLog
from game.component.movement import Position
from game.component.player import GUTPlayerBump, Player
from game.events import (
    InputEvent,
    ChooseFromListEvent,
    ChoiceFromListEvent,
    ChoiceAcceptedEvent,
    ChoiceDeclinedEvent,
    MenuClosedEvent,
    SubMenuClosedEvent,
)
from game.types import EventType, GameState, EquipType, Entity
from game.utils.geometry import Point
from gamedata.palette import ItemPalette, MessagePalette

KEYS_JSON = Path("data") / Path("keys.json")
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class PlayerInputProcessor(esper.Processor):
    """Process user input and issue events."""

    def __init__(self) -> None:
        super().__init__()
        self.input_queue: list = []
        InputEvent.handle(self._on_input)
        with open(KEYS_JSON) as f:
            keys: dict = json.load(f)
        self.keys: dict = keys["Keys"]
        self.keys_reverse: dict = {v: k for k, v in self.keys.items()}
        self.modifiers: dict = keys["Modifiers"]
        self.events: dict = keys["Events"]

    def _on_input(self, event: EventType) -> None:
        modifiers: dict = self._unpack_modifiers(event["modifiers"])
        key: str = self._get_key(event["code"])
        coords: Point = Point(event["x_coord"], event["y_coord"])
        self.input_queue.append(
            {
                "event": event["event"],
                "state": event.get("state", GameState.unknown),
                "modifiers": modifiers,
                "key": key,
                "coords": coords,
            }
        )

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process the input queue."""
        while self.input_queue:
            event = self.input_queue.pop()
            if event["event"] == self.events["KeyPress"]:
                if event["state"] == GameState.playing:
                    self.handle_keypress_playing(event["modifiers"], event["key"], event["coords"])

    def _unpack_modifiers(self, modifiers: int) -> dict:
        return {
            "shift": modifiers & self.modifiers["Shift"] != 0,
            "ctrl": modifiers & self.modifiers["Ctrl"] != 0,
            "alt": modifiers & self.modifiers["Alt"] != 0,
        }

    def _get_key(self, code: int) -> str:
        try:
            return str(self.keys_reverse[code]).lower()
        except KeyError:
            return chr(code).lower()

    def handle_keypress_playing(self, _modifiers: Mapping, key: str, _coords: Point) -> None:
        """Handle input event in the PLAYING state."""
        handled = self._try_bump(key)
        if not handled:
            handled = self._try_command(key)
        if not handled:
            # TODO: more?
            pass

    def _try_bump(self, key: str) -> bool:
        bump_up = key in "kyu"
        bump_down = key in "jbn"
        bump_left = key in "hyb"
        bump_right = key in "lun"
        wait = key == "period"

        dx = 0
        dy = 0
        if bump_up:
            dy -= 1
        if bump_down:
            dy += 1
        if bump_left:
            dx -= 1
        if bump_right:
            dx += 1

        if not (dx or dy or wait):
            return False

        for ent, _ in self.world.get_component(Player):
            self.world.add_component(ent, GUTPlayerBump(dx, dy))
        return True

    def _try_command(self, key: str) -> bool:
        handled = True
        if key == "comma":
            self._command_pickup()
        elif key == "d":
            self._command_drop()
        elif key == "i":
            self._command_inventory()
        elif key == "e":
            self._command_equip()
        else:
            handled = False
        return handled

    def _get_items_carried(self, ent: Entity) -> dict:
        items_carried: dict = {"equipped": [], "unequipped": []}
        for item_ent, components in self.world.get_components(GUTContained, Name, Containable):
            contained, name, containable = components
            if contained.by_ent == ent:
                if containable.equipped:
                    item_list = items_carried["equipped"]
                else:
                    item_list = items_carried["unequipped"]
                item_list.append(
                    (containable.equip_type.name, contained.label, name.generic, ItemPalette.rare)
                )
        if items_carried["equipped"]:
            items_carried["equipped"].sort()
        else:
            del items_carried["equipped"]
        if items_carried["unequipped"]:
            items_carried["unequipped"].sort()
        else:
            del items_carried["unequipped"]
        return items_carried

    def _command_pickup(self) -> None:
        for ent, _ in self.world.get_component(Player):
            item = self.world.pickup_item(ent)
            if not item:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add(f"There is nothing to pick up!")

    def _command_drop(self) -> None:
        for ent, _ in self.world.get_component(Player):
            pos = self.world.component_for_entity(ent, Position)
            item = self.world.get_item_at_position(pos.x, pos.y)
            if item:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add(
                    "There is already an item on the ground here!", MessagePalette.negative
                )
                return
            items_carried = self._get_items_carried(ent)
            if items_carried:
                ChoiceFromListEvent.handle(self._on_drop_choice)
                MenuClosedEvent.handle(self._on_drop_menu_closed)
                ChooseFromListEvent.fire(
                    {"header": "Drop what?", "items": items_carried, "multiple": True}
                )
            else:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add("You have nothing to drop!")

    def _on_drop_choice(self, event: EventType) -> None:
        modifiers: dict = self._unpack_modifiers(event["modifiers"])
        key: str = self._get_key(event["code"])
        if modifiers["shift"]:
            key = key.upper()
        for ent, _ in self.world.get_component(Player):
            for item_ent, components in self.world.get_components(GUTContained, Name):
                contained, name = components
                if contained.by_ent == ent and contained.label == key:
                    if self.world.drop_item(ent, item_ent):
                        ChoiceAcceptedEvent.fire()
                    else:
                        cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                        cmd_log.add("You can't drop that!")
                        ChoiceDeclinedEvent.fire({"status": "You can't drop that!"})
                    break

    def _on_drop_menu_closed(self, _event: EventType) -> None:
        ChoiceFromListEvent.unhandle(self._on_drop_choice)
        MenuClosedEvent.unhandle(self._on_drop_menu_closed)

    def _command_inventory(self) -> None:
        for ent, _ in self.world.get_component(Player):
            items_carried = self._get_items_carried(ent)
            if items_carried:
                ChoiceFromListEvent.handle(self._on_inventory_choice)
                MenuClosedEvent.handle(self._on_inventory_menu_closed)
                ChooseFromListEvent.fire({"header": "Describe what?", "items": items_carried})
            else:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add("You aren't carrying anything!")

    def _on_inventory_choice(self, event: EventType) -> None:
        modifiers: dict = self._unpack_modifiers(event["modifiers"])
        key: str = self._get_key(event["code"])
        if modifiers["shift"]:
            key = key.upper()
        for ent, _ in self.world.get_component(Player):
            for item_ent, components in self.world.get_components(GUTContained, Name):
                contained, name = components
                if contained.by_ent == ent and contained.label == key:
                    cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                    cmd_log.add("It's ")
                    cmd_log.append(name.generic, ItemPalette.epic)
                    cmd_log.append(".")
                    ChoiceAcceptedEvent.fire()
                    break

    def _on_inventory_menu_closed(self, _event: EventType) -> None:
        ChoiceFromListEvent.unhandle(self._on_inventory_choice)
        MenuClosedEvent.unhandle(self._on_inventory_menu_closed)

    def _command_equip(self) -> None:
        for ent, _ in self.world.get_component(Player):
            items_carried = self._get_items_carried(ent)
            if items_carried:
                ChoiceFromListEvent.handle(self._on_equip_choice)
                MenuClosedEvent.handle(self._on_equip_menu_closed)
                ChooseFromListEvent.fire(
                    {
                        "header": "Equip what?",
                        "items": items_carried,
                        "disable": [EquipType.none.name],
                    }
                )
            else:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add("You have nothing to eqiup!")

    def _on_equip_choice(self, event: EventType) -> None:
        modifiers: dict = self._unpack_modifiers(event["modifiers"])
        key: str = self._get_key(event["code"])
        if modifiers["shift"]:
            key = key.upper()
        for ent, _ in self.world.get_component(Player):
            equipment = self.world.component_for_entity(ent, Equipment)
            want_to_equip = None
            for item_ent, components in self.world.get_components(GUTContained, Name, Containable):
                contained, name, containable = components
                if contained.by_ent == ent and contained.label == key:
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

    def _on_equip_menu_closed(self, _event: EventType) -> None:
        ChoiceFromListEvent.unhandle(self._on_equip_choice)
        MenuClosedEvent.unhandle(self._on_equip_menu_closed)
