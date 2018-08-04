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
        b_cells: bytearray = bytearray()
        num_cells: int = 0
        b_cells.extend(num_cells.to_bytes(2, 'big'))
        for ent, components in sorted(self.world.get_components(Positional, Renderable),
                                      key=lambda x: x[1][1].layer.value):
            positional, renderable = components
            b_cells.extend(ent.to_bytes(2, 'big'))
            b_cells.extend(positional.x.to_bytes(2, 'big'))
            b_cells.extend(positional.y.to_bytes(2, 'big'))
            b_cells.extend(renderable.tile_id.to_bytes(2, 'big'))
            b_cells.extend(renderable.tint.to_bytes(4, 'big'))
            num_cells += 1
        b_cells[:2] = num_cells.to_bytes(2, 'big')
        ##########################################
        # Map Data:
        #     Header:
        #        2 bytes: num cells
        #     Each Cell:
        #        2 bytes: entity id
        #        2 bytes: position x
        #        2 bytes: position y
        #        2 bytes: tile id
        #        3 bytes: tint
        ##########################################
        # TODO: improve performance by sending message less often
        WebsocketWriteAllEvent.fire({'message': bytes(b_cells), 'binary': True})


class TCODRenderProcessor(esper.Processor):
    """Game render processor for local TCOD console."""

    def __init__(self, title: str, width: int=80, height: int=40) -> None:
        super().__init__()
        # Someday, implement this?
        print("Wouldn't that be nice?")

    def process(self, *args: Any) -> None:
        """Process all renderables."""
        pass
