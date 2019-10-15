"""Render components."""
import dataclasses
import typing

import game.palette
import game.types


@dataclasses.dataclass
class Renderable:
    """Renderable component."""

    tile: typing.Tuple[str, str]
    tint: game.palette.Base
    remembered: bool = False  # if True, the player remembers where it was
    last_seen_x: int = 0
    last_seen_y: int = 0
    last_seen_facing: str = ""
