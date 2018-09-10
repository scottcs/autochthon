"""Render processors."""
import logging
from typing import Any

import esper
import tcod

from game.component.status import Dead
from game.component.player import PlayerControlled
from game.component.movement import Position
from game.component.render import Renderable
from game.events import UpdateMapRenderEvent
from gamedata.palette import Palette

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
        self.world.map.compute_fov(player_x, player_y,
                                   algorithm=tcod.FOV_BASIC,
                                   radius=7,  # TODO: make part of a component/vision stat
                                   light_walls=True)
        for cell in self.world.map:
            data_length += 1
            # WARNING: this will override any entities with ID >= 10000!
            #          also limits map size to about 235x235
            cell_id = 10000 + self.world.map.width * cell.x + cell.y
            b_cells.extend(cell_id.to_bytes(2, 'big'))
            b_cells.extend(cell.x.to_bytes(2, 'big'))
            b_cells.extend(cell.y.to_bytes(2, 'big'))
            tile_id = cell.tile_id
            color = cell.tile_color
            alpha = 0x00

            if cell.spawnable_player:
                # TODO: move this to map
                tile_id = 229
                color = Palette.cyan

            if cell.explored:
                alpha = 0x60
            if cell.fov:
                self.world.map.explored[cell.y, cell.x] = True
                alpha = 0xff

            b_cells.extend(tile_id.to_bytes(2, 'big'))
            b_cells.extend(color.to_bytes(3, 'big'))
            b_cells.extend(alpha.to_bytes(1, 'big'))

        # RENDERABLE ENTITIES
        for ent, components in sorted(self.world.get_components(Position, Renderable),
                                      key=lambda x: x[1][1].layer.value):
            positional, renderable = components
            alpha = 0x00
            pos_x = positional.x
            pos_y = positional.y
            can_see_now = self.world.map.fov[positional.y, positional.x]
            seen = renderable.last_seen_x is not None
            can_see_prev = seen and self.world.map.fov[renderable.last_seen_y,
                                                       renderable.last_seen_x]
            # if we can see it now, draw it and update seen pos
            if can_see_now:
                alpha = 0xff
                renderable.last_seen_x = positional.x
                renderable.last_seen_y = positional.y
            # else if we've seen it, and we can't see where it last was, draw it faded and remember
            elif seen and not can_see_prev:
                alpha = 0x60
                pos_x = renderable.last_seen_x
                pos_y = renderable.last_seen_y
            # else if we can see where it last was, forget where we've seen it and don't draw it
            elif can_see_prev:
                renderable.last_seen_x = None
                renderable.last_seen_y = None
            # else don't draw it

            b_cells.extend(ent.to_bytes(2, 'big'))
            b_cells.extend(pos_x.to_bytes(2, 'big'))
            b_cells.extend(pos_y.to_bytes(2, 'big'))
            if self.world.has_component(ent, Dead):
                tile_id = 0
            else:
                tile_id = renderable.tile_id
            b_cells.extend(tile_id.to_bytes(2, 'big'))
            b_cells.extend(renderable.tint.to_bytes(3, 'big'))
            b_cells.extend(alpha.to_bytes(1, 'big'))
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
        #        1 byte : alpha
        ##########################################
        UpdateMapRenderEvent.fire({'bytearray': b_cells})


class TCODRenderProcessor(esper.Processor):
    """Game render processor for local TCOD console."""

    def __init__(self, _title: str, width: int=80, height: int=40) -> None:
        super().__init__()
        # Someday, implement this?
        log.error(f'Someday maybe this will be a {width}x{height} console.')

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process all renderables."""
        pass
