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
            input_key = game.types.InputKey(
                blt.read(),
                blt.check(blt.TK_SHIFT),
                blt.check(blt.TK_CONTROL),
                blt.check(blt.TK_ALT),
            )
            state: game.types.GameState = kwargs.pop("state")
            try:
                {game.types.GameState.playing: self._handle_state_playing}[state](input_key)
            except KeyError:
                self._handle_default(input_key)

    def _handle_state_playing(self, input_key: game.types.InputKey) -> None:
        handled = self._try_bump(input_key)
        if not handled:
            handled = self._try_command(input_key)
        if not handled:
            # TODO: more?
            # TODO: remove this (quit through menu)
            self._handle_default(input_key)

    @staticmethod
    def _handle_default(input_key: game.types.InputKey) -> None:
        if game.utils.input.GameInterface.match("quit", input_key):
            game.events.GameOver({"shutdown": True})

    def _try_bump(self, input_key: game.types.InputKey) -> bool:
        dx = 0
        dy = 0
        wait = game.utils.input.GameCommand.match("wait", input_key)

        if not wait:
            bump_up = game.utils.input.GameMovement.match_any(["nw", "n", "ne"], input_key)
            bump_down = game.utils.input.GameMovement.match_any(["sw", "s", "se"], input_key)
            bump_left = game.utils.input.GameMovement.match_any(["nw", "w", "sw"], input_key)
            bump_right = game.utils.input.GameMovement.match_any(["ne", "e", "se"], input_key)

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

    def _try_command(self, input_key: game.types.InputKey) -> bool:
        handled = True
        command = game.utils.input.GameCommand.from_key_code(input_key)
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
