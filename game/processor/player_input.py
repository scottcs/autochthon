"""User input processing."""
import logging
import typing

import bearlibterminal.terminal as blt
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

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process the input queue."""
        if blt.has_input():
            key_code = blt.read()
            state: game.types.GameState = kwargs.pop("state")
            try:
                {game.types.GameState.playing: self._handle_state_playing}[state](key_code)
            except KeyError:
                self._handle_default(key_code)

    def _handle_state_playing(self, key_code: int) -> None:
        handled = self._try_bump(key_code)
        if not handled:
            handled = self._try_command(key_code)
        if not handled:
            # TODO: more?
            # TODO: remove this (quit through menu)
            self._handle_default(key_code)

    @staticmethod
    def _handle_default(key_code: int) -> None:
        if game.utils.input.GameInterface.match("quit", key_code):
            game.events.GameOver({"shutdown": True})

    def _try_bump(self, key_code: int) -> bool:
        if blt.check(blt.TK_SHIFT) or blt.check(blt.TK_ALT) or blt.check(blt.TK_CONTROL):
            return False

        dx = 0
        dy = 0
        wait = game.utils.input.GameCommand.match("wait", key_code)

        if not wait:
            bump_up = game.utils.input.GameMovement.match_any(["nw", "n", "ne"], key_code)
            bump_down = game.utils.input.GameMovement.match_any(["sw", "s", "se"], key_code)
            bump_left = game.utils.input.GameMovement.match_any(["nw", "w", "sw"], key_code)
            bump_right = game.utils.input.GameMovement.match_any(["ne", "e", "se"], key_code)

            if bump_up:
                dy -= 1
            if bump_down:
                dy += 1
            if bump_left:
                dx -= 1
            if bump_right:
                dx += 1

            if not (dx or dy):
                return False

        for ent, _ in self.world.get_component(game.component.player.Player):
            self.world.add_component(ent, game.component.player.TMPPlayerBump(dx, dy))
        return True

    def _try_command(self, key_code: int) -> bool:
        handled = True
        command = game.utils.input.GameCommand.from_key_code(key_code)
        if command is None:
            handled = False
        else:
            try:
                {
                    "pick_up": game.command.pickup.Pickup,
                    "drop": game.command.drop.Drop,
                    "inventory": game.command.inventory.Inventory,
                    "equip": game.command.equip.Equip,
                }[command](self.world).run()
            except KeyError:
                handled = False
        return handled
