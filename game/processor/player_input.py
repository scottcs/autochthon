"""User input processing."""
import logging
import typing

import esper

import game.command.drop
import game.command.equip
import game.command.inventory
import game.command.pickup
import game.component.player
import game.events
import game.types
import game.utils.geometry
import game.utils.input

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class PlayerInput(esper.Processor):
    """Process user input and issue events."""

    def __init__(self) -> None:
        self.input_queue: list = []
        game.events.Input.handle(self._on_input)

    def _on_input(self, event: game.types.EventType) -> None:
        modifiers: dict = game.utils.input.unpack_modifiers(event["modifiers"])
        key: str = game.utils.input.get_key(event["code"])
        coords: game.utils.geometry.Point = game.utils.geometry.Point(
            event["x_coord"], event["y_coord"]
        )
        self.input_queue.append(
            {
                "event": event["event"],
                "state": event.get("state", game.types.GameState.unknown),
                "modifiers": modifiers,
                "key": key,
                "coords": coords,
            }
        )

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process the input queue."""
        while self.input_queue:
            event = self.input_queue.pop()
            if event["event"] == game.utils.input.events["KeyPress"]:
                if event["state"] == game.types.GameState.playing:
                    self.handle_keypress_playing(event["modifiers"], event["key"], event["coords"])

    def handle_keypress_playing(
        self, _modifiers: typing.Mapping, key: str, _coords: game.utils.geometry.Point
    ) -> None:
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

        for ent, _ in self.world.get_component(game.component.player.Player):
            self.world.add_component(ent, game.component.player.GUTPlayerBump(dx, dy))
        return True

    def _try_command(self, key: str) -> bool:
        handled = True
        if key == "comma":
            game.command.pickup.Pickup(self.world).run()
        elif key == "d":
            game.command.drop.Drop(self.world).run()
        elif key == "i":
            game.command.inventory.Inventory(self.world).run()
        elif key == "e":
            game.command.equip.Equip(self.world).run()
        else:
            handled = False
        return handled
