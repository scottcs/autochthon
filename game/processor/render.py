"""Render processors."""
from typing import Any

import esper

from game.component.positional import Positional
from game.component.renderable import Renderable
from game.events import WebsocketWriteAllEvent
from game.types import GameMapCellData, GameMapData


class WebRenderProcessor(esper.Processor):
    """Game render processor for web socket."""

    def __init__(self) -> None:
        super().__init__()

    def process(self, *args: Any) -> None:
        """Process all renderables."""
        map_data: GameMapData = {}
        cells: GameMapCellData = []
        for ent, components in sorted(self.world.get_components(Positional, Renderable),
                                      key=lambda x: x[1][1].layer):
            positional, renderable = components
            cells.append([ent, positional.x, positional.y, renderable.tile_id, renderable.tint])
        map_data['cells'] = cells
        WebsocketWriteAllEvent.fire({'map': map_data})


class TCODRenderProcessor(esper.Processor):
    """Game render processor for local TCOD console."""

    def __init__(self, title: str, width: int=80, height: int=40) -> None:
        super().__init__()
        # Someday, implement this?
        print("Wouldn't that be nice?")

    def process(self, *args: Any) -> None:
        """Process all renderables."""
        pass
