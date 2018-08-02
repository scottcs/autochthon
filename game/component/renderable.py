"""Renderable component."""


class Renderable:
    """Renderable component."""
    def __init__(self, tile_id: int, tint: int, layer: int) -> None:
        self.tile_id: int = tile_id
        self.tint: int = tint
        self.layer: int = layer
