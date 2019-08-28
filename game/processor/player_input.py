"""User input processing."""
import logging
from typing import Any, Mapping

import esper

from game.command.drop import DropCommand
from game.command.equip import EquipCommand
from game.command.pickup import PickupCommand
from game.command.inventory import InventoryCommand
from game.component.player import GUTPlayerBump, Player
from game.events import InputEvent
from game.types import EventType, GameState
from game.utils.geometry import Point
from game.utils.input import events, unpack_modifiers, get_key

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class PlayerInputProcessor(esper.Processor):
    """Process user input and issue events."""

    def __init__(self) -> None:
        self.input_queue: list = []
        InputEvent.handle(self._on_input)

    def _on_input(self, event: EventType) -> None:
        modifiers: dict = unpack_modifiers(event["modifiers"])
        key: str = get_key(event["code"])
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
            if event["event"] == events["KeyPress"]:
                if event["state"] == GameState.playing:
                    self.handle_keypress_playing(event["modifiers"], event["key"], event["coords"])

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
            PickupCommand(self.world).run()
        elif key == "d":
            DropCommand(self.world).run()
        elif key == "i":
            InventoryCommand(self.world).run()
        elif key == "e":
            EquipCommand(self.world).run()
        else:
            handled = False
        return handled
