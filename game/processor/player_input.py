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
        key_code = blt.read()
        if key_code == blt.TK_ESCAPE:
            game.events.GameOver({"shutdown": True})
