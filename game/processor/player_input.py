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

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class PlayerInput(esper.Processor):
    """Process user input and issue events."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process the input queue."""
        state: game.types.GameState = kwargs.pop("state")
        key_code = blt.read()
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
        if key_code == blt.TK_ESCAPE:
            game.events.GameOver({"shutdown": True})

    def _try_bump(self, key_code: int) -> bool:
        if blt.check(blt.TK_SHIFT) or blt.check(blt.TK_ALT) or blt.check(blt.TK_CONTROL):
            return False

        bump_up = key_code in (blt.TK_K, blt.TK_Y, blt.TK_U)
        bump_down = key_code in (blt.TK_J, blt.TK_B, blt.TK_N)
        bump_left = key_code in (blt.TK_H, blt.TK_Y, blt.TK_B)
        bump_right = key_code in (blt.TK_L, blt.TK_U, blt.TK_N)
        wait = key_code == blt.TK_PERIOD

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

    def _try_command(self, key_code: int) -> bool:
        handled = True
        try:
            {
                blt.TK_COMMA: game.command.pickup.Pickup,
                blt.TK_D: game.command.drop.Drop,
                blt.TK_I: game.command.inventory.Inventory,
                blt.TK_E: game.command.equip.Equip,
            }[key_code](self.world).run()
        except KeyError:
            handled = False
        return handled
