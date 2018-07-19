"""Renderable component."""


class Renderable:
    """Renderable component."""
    def __init__(self, tile_id, x, y, tint, layer):
        self.x, self.y = x, y
        self.tile_id = tile_id
        self.tint = tint
        self.layer = layer
