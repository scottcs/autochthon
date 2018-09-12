"""User input processing."""
import json
import logging
from pathlib import Path
from typing import Any, Mapping

import esper

from game.component.container import Containable, Container, GUTContained
from game.component.descriptive import Name
from game.component.gamelog import GUTCommandLog
from game.component.movement import Position
from game.component.player import GUTPlayerBump, PlayerControlled
from game.events import InputEvent, RefreshMapEvent, ChooseFromListEvent
from game.types import EventType, GameState, EquipType
from game.utils.geometry import Point
from gamedata.palette import ItemPalette, MessagePalette

KEYS_JSON = Path("data") / Path("keys.json")
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


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

        for ent, _ in self.world.get_component(PlayerControlled):
            self.world.add_component(ent, GUTPlayerBump(dx, dy))
        return True

    def _try_command(self, key: str) -> bool:
        handled = False
        if key == "comma":
            self._command_pickup()
            handled = True
        elif key == "d":
            # TODO: send message to client with item list and wait for response of choice (or none)
            # TODO: drop item if chosen
            log.error("IMPLEMENT DROP")
            for ent, _ in self.world.get_component(PlayerControlled):
                items_carried = []
                for item_ent, components in self.world.get_components(GUTContained, Name):
                    contained, name = components
                    if contained.ent == ent:
                        # TODO: item rarity
                        items_carried.append((name.generic, ItemPalette.rare))
                if items_carried:
                    # TODO: send prompt
                    ChooseFromListEvent.fire(items_carried)
                else:
                    cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                    cmd_log.add("You have nothing to drop!")
        return handled

    def _command_pickup(self) -> None:
        for ent, _ in self.world.get_component(PlayerControlled):
            at = self.world.component_for_entity(ent, Position)
            cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
            item_ent = self.world.get_entity_at_position(at.x, at.y, Position, Containable)
            if item_ent:
                container = self.world.component_for_entity(ent, Container)
                item = self.world.component_for_entity(item_ent, Containable)
                if container.equip_type != EquipType.none and (
                        container.equip_type == EquipType.any
                        or container.equip_type == item.equip_type
                        or item.equip_type == EquipType.any
                ):
                    seen_slots = set()
                    for ie, contained in self.world.get_component(GUTContained):
                        if contained.ent == ent and contained.component_class == Container:
                            seen_slots.add(contained.slot)
                    if len(seen_slots) < container.max_slots:
                        for slot in range(container.max_slots):
                            if slot not in seen_slots:
                                self.world.remove_component(item_ent, Position)
                                self.world.add_component(
                                    item_ent, GUTContained(ent, Container, slot)
                                )
                                name = self.world.component_for_entity(item_ent, Name)
                                # TODO: colorize the item by rarity?
                                cmd_log.add(f"You pick up ")
                                cmd_log.append(f"{name.generic}", color=ItemPalette.epic)
                                cmd_log.append(".")
                                RefreshMapEvent.fire()
                                break
                    else:
                        cmd_log.add(f"{container.name} is full.")
                else:
                    cmd_log.add(f"{container.name} can't hold that.")
            else:
                cmd_log.add(f"There is nothing to pick up!")
