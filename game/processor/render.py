"""Render processors."""
import logging
import typing

import bearlibterminal.terminal as blt
import esper

import game.constants.config

MAP_BITS = game.constants.config.CONFIG["map_bits"]
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class BearLibRender(esper.Processor):
    """Game render processor for BearLibTerminal console."""

    def __init__(self, title: str, width: int, height: int) -> None:
        blt.set(f"window: size={width}x{height}, title={title}")
        if not blt.open():
            log.critical("Unable to initialize terminal window!")
        blt.puts(4, 4, "Test")

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process all renderables."""
        blt.refresh()
