"""Render components."""
import dataclasses
import typing

import game.constants.palette
import game.types


@dataclasses.dataclass
class Renderable:
    """Renderable component."""

    tile_id: int
    tint: game.constants.palette.Base
    layer: game.types.RenderLayer

    def __post_init__(self) -> None:
        self.last_seen_x: typing.Optional[int] = None
        self.last_seen_y: typing.Optional[int] = None
