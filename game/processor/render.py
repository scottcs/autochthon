"""Render processors."""
import logging
from typing import Any, Dict

import esper
import tcod

from game.component.status import GUTDead
from game.component.player import Player
from game.component.movement import Position
from game.component.render import Renderable
from game.events import UpdateMapRenderEvent
from game.types import RenderLayer
from gamedata.palette import Palette
from gamedata.config import CONFIG

MAP_BITS = CONFIG["map_bits"]
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class WebRenderProcessor(esper.Processor):
    """Game render processor for web socket."""

    def __init__(self) -> None:
        super().__init__()
        self.cache: Dict[str, Any] = {"player_x": -1, "player_y": -1, "cells": {}}

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process all renderables."""
        b_cells: bytearray = bytearray()
        data_length: int = 0
        player_x: int = 0
        player_y: int = 0
        fov: int = 1

        # PLAYER POSITION
        for ent, components in self.world.get_components(Player, Renderable, Position):
            position = components[-1]
            player_x = position.x
            player_y = position.y
            fov = components[0].fov
            # TODO: handle more than one player controlled object?
            break

        # HEADER
        b_cells.extend(player_x.to_bytes(2, "big"))
        b_cells.extend(player_y.to_bytes(2, "big"))
        b_cells.extend(data_length.to_bytes(2, "big"))

        # MAP
        if player_x != self.cache["player_x"] or player_y != self.cache["player_y"]:
            self.world.map.compute_fov(
                player_x, player_y, algorithm=tcod.FOV_PERMISSIVE_3, radius=fov, light_walls=True
            )
        self.cache["player_x"] = player_x
        self.cache["player_y"] = player_y

        for y, x in self.world.map:
            alpha = 0x00
            if self.world.map.explored[y, x]:
                alpha = 0x60
            if self.world.map.fov[y, x]:
                self.world.map.explored[y, x] = True
                alpha = 0xff
            if alpha == 0:
                continue

            tile_id, color = self.world.map.get_tile(y, x)

            # WARNING: this will override any entities with ID >= 10000!
            #          also limits map size to about 235x235
            cell_id = 10000 + y + self.world.map.width * x
            layer = RenderLayer.floor.value

            if self.world.map.spawnable_player[y, x]:
                # TODO: move this to map
                tile_id = 229
                color = Palette.cyan

            if not self.world.map.walkable[y, x]:
                # TODO: other layers (debris, decoration)
                layer = RenderLayer.wall.value

            cell_cache = self.cache["cells"].get(cell_id, None)
            if cell_cache is None:
                bitmask = (
                    MAP_BITS["x"]
                    | MAP_BITS["y"]
                    | MAP_BITS["tile_id"]
                    | MAP_BITS["tint"]
                    | MAP_BITS["alpha"]
                    | MAP_BITS["layer"]
                )
                self.cache["cells"][cell_id] = {
                    "x": x,
                    "y": y,
                    "tile_id": tile_id,
                    "tint": color,
                    "alpha": alpha,
                    "layer": layer,
                }
            else:
                bitmask = 0
                if cell_cache["x"] != x:
                    bitmask |= MAP_BITS["x"]
                    cell_cache["x"] = x
                if cell_cache["y"] != y:
                    bitmask |= MAP_BITS["y"]
                    cell_cache["y"] = y
                if cell_cache["tile_id"] != tile_id:
                    bitmask |= MAP_BITS["tile_id"]
                    cell_cache["tile_id"] = tile_id
                if cell_cache["tint"] != color:
                    bitmask |= MAP_BITS["tint"]
                    cell_cache["tint"] = color
                if cell_cache["alpha"] != alpha:
                    bitmask |= MAP_BITS["alpha"]
                    cell_cache["alpha"] = alpha
                if cell_cache["layer"] != layer:
                    bitmask |= MAP_BITS["layer"]
                    cell_cache["layer"] = layer

            if bitmask > 0:
                b_cells.extend(cell_id.to_bytes(2, "big"))
                b_cells.extend(bitmask.to_bytes(1, "big"))
                if bitmask & MAP_BITS["x"]:
                    b_cells.extend(self.cache["cells"][cell_id]["x"].to_bytes(2, "big"))
                if bitmask & MAP_BITS["y"]:
                    b_cells.extend(self.cache["cells"][cell_id]["y"].to_bytes(2, "big"))
                if bitmask & MAP_BITS["tile_id"]:
                    b_cells.extend(self.cache["cells"][cell_id]["tile_id"].to_bytes(2, "big"))
                if bitmask & MAP_BITS["tint"]:
                    b_cells.extend(self.cache["cells"][cell_id]["tint"].to_bytes(3, "big"))
                if bitmask & MAP_BITS["alpha"]:
                    b_cells.extend(self.cache["cells"][cell_id]["alpha"].to_bytes(1, "big"))
                if bitmask & MAP_BITS["layer"]:
                    b_cells.extend(self.cache["cells"][cell_id]["layer"].to_bytes(1, "big"))
                data_length += 1

        # RENDERABLE ENTITIES
        for ent, components in sorted(
            self.world.get_components(Position, Renderable), key=lambda t: t[1][1].layer.value
        ):
            positional, renderable = components
            alpha = 0x00
            pos_y = positional.y
            pos_x = positional.x
            can_see_now = self.world.map.fov[positional.y, positional.x]
            if renderable.last_seen_x is None:
                seen = False
                can_see_prev = False
            else:
                seen = True
                can_see_prev = self.world.map.fov[renderable.last_seen_y, renderable.last_seen_x]

            # if we can see it now, draw it and update seen pos
            if can_see_now:
                alpha = 0xff
                renderable.last_seen_y = positional.y
                renderable.last_seen_x = positional.x
            # else if we can see where it last was, forget where we've seen it and don't draw it
            elif can_see_prev:
                renderable.last_seen_y = None
                renderable.last_seen_x = None
            # else if we've seen it, draw it faded where we last saw it
            elif seen:
                alpha = 0x60
                pos_y = renderable.last_seen_y
                pos_x = renderable.last_seen_x
            # else don't draw it

            if alpha == 0:
                continue

            if self.world.has_component(ent, GUTDead):
                bitmask = MAP_BITS["delete"]
            else:
                bitmask = (
                    MAP_BITS["x"]
                    | MAP_BITS["y"]
                    | MAP_BITS["tile_id"]
                    | MAP_BITS["tint"]
                    | MAP_BITS["alpha"]
                    | MAP_BITS["layer"]
                )
            if bitmask > 0:
                b_cells.extend(ent.to_bytes(2, "big"))
                b_cells.extend(bitmask.to_bytes(1, "big"))
                if bitmask & MAP_BITS["x"]:
                    b_cells.extend(pos_x.to_bytes(2, "big"))
                if bitmask & MAP_BITS["y"]:
                    b_cells.extend(pos_y.to_bytes(2, "big"))
                if bitmask & MAP_BITS["tile_id"]:
                    b_cells.extend(renderable.tile_id.to_bytes(2, "big"))
                if bitmask & MAP_BITS["tint"]:
                    b_cells.extend(renderable.tint.to_bytes(3, "big"))
                if bitmask & MAP_BITS["alpha"]:
                    b_cells.extend(alpha.to_bytes(1, "big"))
                if bitmask & MAP_BITS["layer"]:
                    b_cells.extend(renderable.layer.value.to_bytes(1, "big"))
                data_length += 1

        # Overwrite data_length now that we've counted them
        b_cells[4:6] = data_length.to_bytes(2, "big")
        ##########################################
        # Map Data:
        #     Header:
        #        2 bytes: player x position
        #        2 bytes: player y position
        #        2 bytes: num cells
        #     Each Cell:
        #        2 bytes: entity id
        #        1 byte: bitmask of what changed
        #        2 bytes: position x if it changed
        #        2 bytes: position y if it changed
        #        2 bytes: tile id if it changed
        #        3 bytes: tint if it changed
        #        1 byte : alpha if it changed
        #        1 byte : render layer if it changed
        #
        # Bitmask:
        #   1 - position x
        #   2 - position y
        #   4 - tile id
        #   8 - tint
        #   16 - alpha
        #   32 - render layer
        #   64 - ?
        #   128 - ?
        #
        # So:    header = 6 bytes
        #     each cell = 3 bytes + (1-11 bytes) = 4-14 bytes, but usually 4-5 bytes
        # AND we only send a cell if something has changed.
        ##########################################
        UpdateMapRenderEvent.fire({"bytearray": b_cells})


class TCODRenderProcessor(esper.Processor):
    """Game render processor for local TCOD console."""

    def __init__(self, _title: str, width: int = 80, height: int = 40) -> None:
        super().__init__()
        # Someday, implement this?
        log.error(f"Someday maybe this will be a {width}x{height} console.")

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process all renderables."""
        pass
