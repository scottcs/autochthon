"""Render processors."""
import logging
from typing import Any

import esper

from game.component.status import Dead
from game.component.player import PlayerControlled
from game.component.movement import Position
from game.component.render import Renderable
from game.events import WebsocketWriteAllEvent

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class WebRenderProcessor(esper.Processor):
    """Game render processor for web socket."""

    def __init__(self) -> None:
        super().__init__()

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process all renderables."""
        b_cells: bytearray = bytearray()
        data_length: int = 0
        player_x: int = 0
        player_y: int = 0

        # PLAYER POSITION
        for ent, components in self.world.get_components(PlayerControlled, Renderable, Position):
            position = components[-1]
            player_x = position.x
            player_y = position.y
            # TODO: handle more than one player controlled object?
            break

        # HEADER
        b_cells.extend(player_x.to_bytes(2, 'big'))
        b_cells.extend(player_y.to_bytes(2, 'big'))
        b_cells.extend(data_length.to_bytes(2, 'big'))

        # MAP
        for cell in self.world.map:
            data_length += 1
            # WARNING: this will override any entities with ID >= 10000!
            #          also limits map size to about 235x235
            cell_id = 10000 + self.world.map.width * cell.x + cell.y
            b_cells.extend(cell_id.to_bytes(2, 'big'))
            b_cells.extend(cell.x.to_bytes(2, 'big'))
            b_cells.extend(cell.y.to_bytes(2, 'big'))
            if cell.walkable:
                b_cells.extend(self.world.map.floor_tile_id.to_bytes(2, 'big'))
                b_cells.extend(self.world.map.floor_color.to_bytes(4, 'big'))
            else:
                b_cells.extend(self.world.map.wall_tile_id.to_bytes(2, 'big'))
                b_cells.extend(self.world.map.wall_color.to_bytes(4, 'big'))

        # RENDERABLE ENTITIES
        for ent, components in sorted(self.world.get_components(Position, Renderable),
                                      key=lambda x: x[1][1].layer.value):
            positional, renderable = components
            b_cells.extend(ent.to_bytes(2, 'big'))
            b_cells.extend(positional.x.to_bytes(2, 'big'))
            b_cells.extend(positional.y.to_bytes(2, 'big'))
            if self.world.has_component(ent, Dead):
                tile_id = 0
            else:
                tile_id = renderable.tile_id
            b_cells.extend(tile_id.to_bytes(2, 'big'))
            b_cells.extend(renderable.tint.to_bytes(4, 'big'))
            data_length += 1
        # Overwrite data_length now that we've counted them
        b_cells[4:6] = data_length.to_bytes(2, 'big')
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


class TCODRenderProcessor(esper.Processor):
    """Game render processor for local TCOD console."""

    def __init__(self, _title: str, width: int=80, height: int=40) -> None:
        super().__init__()
        # Someday, implement this?
        log.error(f'Someday maybe this will be a {width}x{height} console.')

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process all renderables."""
        pass
