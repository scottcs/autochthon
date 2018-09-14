"""Render components."""
from dataclasses import dataclass
from typing import Optional

from game.types import RenderLayer
from gamedata.palette import Palette


@dataclass
class Renderable:
    """Renderable component."""

    tile_id: int
    tint: Palette
    layer: RenderLayer

    def __post_init__(self) -> None:
        self.last_seen_x: Optional[int] = None
        self.last_seen_y: Optional[int] = None
