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

    def __post_init__(self) -> None:
        self.last_seen_x: typing.Optional[int] = None
        self.last_seen_y: typing.Optional[int] = None
        self.last_seen_facing: typing.Optional[str] = None
