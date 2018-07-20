"""Render processors."""
import esper

from game.component.positional import Positional
from game.component.renderable import Renderable


class WebRenderProcessor(esper.Processor):
    """Game render processor for web socket."""

    def __init__(self, socket):
        super().__init__()
        self.socket = socket

    def process(self):
        """Process all renderables."""
        map_data = {}
        cells = []
        for ent, components in sorted(self.world.get_components(Positional, Renderable),
                                      key=lambda x: x[1][1].layer):
            positional, renderable = components
            cells.append([ent, positional.x, positional.y, renderable.tile_id, renderable.tint])
        map_data['cells'] = cells
        self.socket.write_all({'map': map_data})