"""Render processors."""
import logging
from typing import Any, Dict

import esper
import tcod

from game.component.container import GUTContained
from game.component.movement import Position
from game.component.player import Player
from game.component.render import Renderable
from game.component.status import GUTDead
from game.events import RenderEntitiesEvent, RenderMapEvent, UpdateMapRenderEvent
from game.types import EventType, RenderLayer
from gamedata.config import CONFIG
from gamedata.palette import Palette

MAP_BITS = CONFIG["map_bits"]
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class WebRenderProcessor(esper.Processor):
    """Game render processor for web socket."""

    def __init__(self) -> None:
        self.cache: Dict[str, Any] = {"player_x": -1, "player_y": -1, "cells": {}}
        self.render_map: bool = True
        self.render_full_map: bool = True
        self.render_entities: set = set()
        RenderEntitiesEvent.handle(self._on_render_entities)
        RenderMapEvent.handle(self._on_render_map)

    def _on_render_entities(self, event: EventType) -> None:
        entities_to_render = event["entities"]
        if event.get("all", False):
            entities_to_render.extend([ent for ent, _ in self.world.get_components(Renderable)])
        for ent in entities_to_render:
            renderable = self.world.optional_component_for_entity(ent, Renderable)
            if renderable is None:
                log.warning(f"Attempt to render non-renderable entity {ent}")
                continue
            self.render_entities.add((renderable.layer.value, ent))

    def _on_render_map(self, event: EventType) -> None:
        self.render_map = True
        self.render_full_map = event.get("full", False)

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process all renderables."""
        if not (self.render_map or self.render_entities):
            return

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

        if self.render_map:
            data_length += self._append_map_bytes(b_cells, player_x, player_y, fov)
            self.render_map = False
        if self.render_entities:
            data_length += self._append_entity_bytes(b_cells)
            self.render_entities.clear()

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

    def _append_map_bytes(self, b_cells: bytearray, player_x: int, player_y: int, fov: int) -> int:
        self._render_map_if_needed(fov, player_x, player_y)
        self.cache["player_x"] = player_x
        self.cache["player_y"] = player_y

        data_append_length = 0
        for y, x in self.world.map:
            alpha = 0x00
            if self.world.map.explored[y, x]:
                alpha = 0x60
            if self.world.map.fov[y, x]:
                self.world.map.explored[y, x] = True
                alpha = 0xFF
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
            if self.render_full_map or cell_cache is None:
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
                self._append_map_data(b_cells, bitmask, cell_id)
                data_append_length += 1
        self.render_full_map = False
        return data_append_length

    def _append_map_data(self, b_cells, bitmask, cell_id):
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

    def _render_map_if_needed(self, fov, player_x, player_y):
        if self.render_full_map or (
            player_x != self.cache["player_x"] or player_y != self.cache["player_y"]
        ):
            self.world.map.compute_fov(
                player_x, player_y, algorithm=tcod.FOV_PERMISSIVE_3, radius=fov, light_walls=True
            )
            self._add_fov_entities_to_render()

    def _add_fov_entities_to_render(self) -> None:
        for ent, renderable in self.world.get_component(Renderable):
            position = self.world.optional_component_for_entity(ent, Position)
            if position is not None:
                if self.world.map.fov[position.y, position.x]:
                    # we can see it now
                    self.render_entities.add((renderable.layer.value, ent))
            if renderable.last_seen_x is not None:
                # we've seen it before
                self.render_entities.add((renderable.layer.value, ent))

    def _append_entity_bytes(self, b_cells: bytearray) -> int:
        data_append_length = 0
        for _, ent in sorted(self.render_entities):
            renderable = self.world.component_for_entity(ent, Renderable)
            position = self.world.optional_component_for_entity(ent, Position)
            is_dead = self.world.has_component(ent, GUTDead)
            is_contained = self.world.has_component(ent, GUTContained)
            pos_x = pos_y = None
            can_see_now = can_see_prev = seen = False

            if position is not None:
                pos_x = position.x
                pos_y = position.y
                can_see_now = self.world.map.fov[position.y, position.x]

            alpha = 0x00
            if renderable.last_seen_x is not None:
                seen = True
                can_see_prev = self.world.map.fov[renderable.last_seen_y, renderable.last_seen_x]

            # if we can see it now, draw it and update seen pos
            if can_see_now:
                alpha = 0xFF
                renderable.last_seen_y = position.y
                renderable.last_seen_x = position.x
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

            if is_dead or is_contained or position is None:
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
                if pos_x and bitmask & MAP_BITS["x"]:
                    b_cells.extend(pos_x.to_bytes(2, "big"))
                if pos_y and bitmask & MAP_BITS["y"]:
                    b_cells.extend(pos_y.to_bytes(2, "big"))
                if bitmask & MAP_BITS["tile_id"]:
                    b_cells.extend(renderable.tile_id.to_bytes(2, "big"))
                if bitmask & MAP_BITS["tint"]:
                    b_cells.extend(renderable.tint.to_bytes(3, "big"))
                if bitmask & MAP_BITS["alpha"]:
                    b_cells.extend(alpha.to_bytes(1, "big"))
                if bitmask & MAP_BITS["layer"]:
                    b_cells.extend(renderable.layer.value.to_bytes(1, "big"))
                data_append_length += 1
        return data_append_length


class TCODRenderProcessor(esper.Processor):
    """Game render processor for local TCOD console."""

    def __init__(self, _title: str, width: int = 80, height: int = 40) -> None:
        # Someday, implement this?
        log.error(f"Someday maybe this will be a {width}x{height} console.")

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process all renderables."""
        pass
