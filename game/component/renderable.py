"""Renderable component."""


class Renderable:
    """Renderable component."""
    def __init__(self, tileset, tile, x, y, tint, layer):
        self.tileset = tileset
        self.tile = tile
        self.x, self.y = x, y
        self.tint = tint
        self.layer = layer
