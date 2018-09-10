"""Render components."""
from typing import Optional

from game.types import RenderLayer
from gamedata.palette import Palette


class Renderable:
    """Renderable component."""
    def __init__(self, tile_id: int, tint: Palette, layer: RenderLayer) -> None:
        self.tile_id: int = tile_id
        self.tint: Palette = tint
        self.layer: RenderLayer = layer
        self.last_seen_x: Optional[int] = None
        self.last_seen_y: Optional[int] = None
