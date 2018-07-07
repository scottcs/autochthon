"""Renderable component."""


class Renderable:
    """Renderable component."""
    def __init__(self, tileset, tile, x, y):
        self.tileset = tileset
        self.tile = tile
        self.x, self.y = x, y
        self.prev_x, self.prev_y = x, y
