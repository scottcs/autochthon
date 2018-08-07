"""Render processors."""
from typing import Any

import esper

from game.component.positional import Positional
from game.component.renderable import Renderable
from game.events import WebsocketWriteAllEvent, ServerNeedsUpdateEvent
from game.types import EventType


class WebRenderProcessor(esper.Processor):
    """Game render processor for web socket."""

    def __init__(self) -> None:
        super().__init__()
        self.need_to_update: bool = False
        ServerNeedsUpdateEvent.handle(self.on_server_needs_update)

    def on_server_needs_update(self, event: EventType) -> None:
        """Called when server needs to be updated."""
        self.need_to_update = event.get('render', False)

    def process(self, *args: Any) -> None:
        """Process all renderables."""
        if not self.need_to_update:
            return

        b_cells: bytearray = bytearray()
        num_cells: int = 0
        player_pos = self.world.component_for_entity(self.world.player, Positional)
        b_cells.extend(player_pos.x.to_bytes(2, 'big'))
        b_cells.extend(player_pos.y.to_bytes(2, 'big'))
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
        # Overwrite num_cells now that we've counted them
        b_cells[4:6] = num_cells.to_bytes(2, 'big')
        ##########################################
        # Map Data:
        #     Header:
        #        2 bytes: player x position
        #        2 bytes: player y position
        #        2 bytes: num cells
        #     Each Cell:
        #        2 bytes: entity id
        #        2 bytes: position x
        #        2 bytes: position y
        #        2 bytes: tile id
        #        3 bytes: tint
        ##########################################
        WebsocketWriteAllEvent.fire({'message': bytes(b_cells), 'binary': True})
        self.need_to_update = False


class TCODRenderProcessor(esper.Processor):
    """Game render processor for local TCOD console."""

    def __init__(self, title: str, width: int=80, height: int=40) -> None:
        super().__init__()
        # Someday, implement this?
        print("Wouldn't that be nice?")

    def process(self, *args: Any) -> None:
        """Process all renderables."""
        pass
