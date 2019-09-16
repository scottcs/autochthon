"""Render components."""
import dataclasses
import typing

import game.types
import gamedata.palette


@dataclasses.dataclass
class Renderable:
    """Renderable component."""

    tile_id: int
    tint: gamedata.palette.Palette
    layer: game.types.RenderLayer

    def __post_init__(self) -> None:
        self.last_seen_x: typing.Optional[int] = None
        self.last_seen_y: typing.Optional[int] = None
