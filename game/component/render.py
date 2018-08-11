"""Renderable component."""
from game.types import RenderLayer


class Renderable:
    """Renderable component."""
    def __init__(self, tile_id: int, tint: int, layer: RenderLayer) -> None:
        self.tile_id: int = tile_id
        self.tint: int = tint
        self.layer: RenderLayer = layer
