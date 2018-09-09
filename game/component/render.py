"""Render components."""
from game.types import RenderLayer
from gamedata.palette import Palette


class Renderable:
    """Renderable component."""
    def __init__(self, tile_id: int, tint: Palette, layer: RenderLayer) -> None:
        self.tile_id: int = tile_id
        self.tint: Palette = tint
        self.layer: RenderLayer = layer
