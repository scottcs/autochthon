"""Render processors."""
import logging
import time
import typing

import esper
import tcod

import game.component.container
import game.component.gamelog
import game.component.movement
import game.component.player
import game.component.render
import game.component.status
import game.data
import game.events
import game.palette
import game.render
import game.types
import game.utils.geometry

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# 1 second = 1 billion nanoseconds
NS = 1_000_000_000
# animate a frame every quarter of a second
ANIM_FRAME_TIME = NS // 4
# maximum number of frames in an animation
MAX_ANIM_FRAMES = 8


class Render(esper.Processor):
    """Game render processor for BearLibTerminal console."""

    def __init__(self, renderer: game.render.BaseRenderer) -> None:
        self.renderer = renderer
        self.last_process_time: int = time.time_ns()
        self.anim_tick: int = 0
        self.should_render_map: bool = True
        self.should_render_entities: bool = True
        self.known_player_xy: typing.List[int] = [-1, -1]

        game.events.RenderEntities.handle(self._on_render_entities)
        game.events.RenderMap.handle(self._on_render_map)
        game.events.GameLog.handle(self._on_game_log)
        game.events.GameOver.handle(self._on_game_over)

        self._draw_debug_overlay()

    def _draw_debug_overlay(self):
        # debug_tile_id = game.render.TileCache.get("world", "floor_tile2", variant=2)
        # debug_tile_id2 = game.render.TileCache.get("world", "floor_tile3", variant=2)
        # tile_width = game.render.grid_to_tile_x("world", self.renderer.width)
        # tile_height = game.render.grid_to_tile_y("world", self.renderer.height)
        # tile_center_x = game.render.grid_to_tile_x("world", self.renderer.center[0])
        # tile_center_y = game.render.grid_to_tile_y("world", self.renderer.center[1])
        # log.debug(f"tile_w/h: {tile_width}x{tile_height} c: {tile_center_x}, {tile_center_y}")
        # for x in range(tile_width):
        #     for y in range(tile_height):
        #         do_x = x in (0, tile_width - 1, tile_center_x)
        #         do_y = y in (0, tile_height - 1, tile_center_y)
        #         if do_x or do_y:
        #             tile_id = (x + y) % 2 == 0 and debug_tile_id or debug_tile_id2
        #             draw_x = game.render.snap_tile_to_grid_x("world", x)
        #             draw_y = game.render.snap_tile_to_grid_y("world", y)
        #             self.renderer.draw_on_layer(
        #                 game.types.RenderLayer.debug, draw_x, draw_y, tile_id
        #             )
        for x in range(self.renderer.width):
            self.renderer.draw_text_on_layer(
                game.types.RenderLayer.debug + 1, x, self.renderer.center[1], "-", color="red"
            )

        for y in range(self.renderer.height):
            self.renderer.draw_text_on_layer(
                game.types.RenderLayer.debug + 1, self.renderer.center[0], y, "|", color="red"
            )

        self.renderer.draw_text_on_layer(
            game.types.RenderLayer.debug + 1,
            self.renderer.center[0],
            self.renderer.center[1],
            "+",
            color="red",
        )

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process all renderables."""
        elapsed = time.time_ns() - self.last_process_time
        if elapsed >= ANIM_FRAME_TIME:
            self.last_process_time = time.time_ns()
            self.anim_tick = (self.anim_tick + 1) % MAX_ANIM_FRAMES
            self.should_render_entities = True

        refresh = False
        player_data = self._get_player_render_data()
        border: int = 1
        tile_viewport = game.utils.geometry.Rect(
            game.render.grid_to_tile_x(
                "world", int(border * game.render.get_conversion_value("world", 0))
            ),
            game.render.grid_to_tile_y(
                "world", int(border * game.render.get_conversion_value("world", 1))
            ),
            game.render.grid_to_tile_x("world", self.renderer.width) - (border * 2),
            game.render.grid_to_tile_y("world", self.renderer.height) - (border * 2),
        )

        self._update_fov(player_data)
        player_pos = game.utils.geometry.Point(player_data.x, player_data.y)

        if self.should_render_map:
            self._draw_map(tile_viewport, player_pos)
            self.should_render_map = False
            refresh = True
        if self.should_render_entities:
            self._draw_entities(tile_viewport, player_pos)
            self.should_render_entities = False
            refresh = True

        if refresh:
            self.renderer.refresh()

    def _update_fov(self, player_data):
        if [player_data.x, player_data.y] != self.known_player_xy:
            self.world.map.compute_fov(
                player_data.x,
                player_data.y,
                algorithm=tcod.FOV_PERMISSIVE_3,
                radius=player_data.fov,
                light_walls=True,
            )
        self.known_player_xy = [player_data.x, player_data.y]

    def _draw_entities(
        self, tile_viewport: game.utils.geometry.Rect, player_pos: game.utils.geometry.Point
    ) -> None:
        self.renderer.clear_layer(game.types.RenderLayer.enemy)
        self.renderer.clear_layer(game.types.RenderLayer.item)
        self.renderer.clear_layer(game.types.RenderLayer.player)

        map_x1: int = player_pos.x - tile_viewport.center.x
        map_y1: int = player_pos.y - tile_viewport.center.y

        for ent, components in self.world.get_components(
            game.component.render.Renderable, game.component.movement.Position
        ):
            renderable, position = components

            is_dead = self.world.has_component(ent, game.component.status.TMPDead)
            is_contained = self.world.has_component(ent, game.component.container.TMPContained)
            if is_dead or is_contained:
                continue

            map_x: typing.Optional[int] = None
            map_y: typing.Optional[int] = None
            facing: typing.Optional[str] = None
            can_see_now: bool = False
            can_see_prev: bool = False
            seen: bool = False

            if position is not None:
                map_x = position.x
                map_y = position.y
                facing = position.facing
                can_see_now = self.world.map.fov[position.y, position.x]

            color = "#00FFFFFF"
            if renderable.last_seen_x is not None and renderable.last_seen_y is not None:
                seen = True
                can_see_prev = self.world.map.fov[renderable.last_seen_y, renderable.last_seen_x]

            # if we can see it now, draw it and update seen pos
            if can_see_now:
                color = "#FFFFFFFF"
                renderable.last_seen_x = position.x
                renderable.last_seen_y = position.y
                renderable.facing = position.facing
            # else if we can see where it last was, forget where we've seen it and don't draw it
            elif can_see_prev:
                renderable.last_seen_y = None
                renderable.last_seen_x = None
                renderable.facing = None
            # else if we've seen it, draw it faded where we last saw it
            elif seen:
                color = "#60FFFFFF"
                map_y = renderable.last_seen_y
                map_x = renderable.last_seen_x
                facing = renderable.last_seen_facing
            # else don't draw it
            else:
                continue

            category, name = renderable.tile
            tile_id = game.render.TileCache.get(
                category, name, direction=facing, frame=self.anim_tick
            )
            if map_x is not None and map_y is not None:
                adjusted_x: int = map_x - map_x1
                adjusted_y: int = map_y - map_y1
                if (
                    adjusted_x < tile_viewport.x1
                    or adjusted_x > tile_viewport.x2
                    or adjusted_y < tile_viewport.y1
                    or adjusted_y > tile_viewport.y2
                ):
                    continue

                draw_x = game.render.snap_tile_to_grid_x(category, adjusted_x)
                draw_y = game.render.snap_tile_to_grid_y(category, adjusted_y)
                if 0 <= draw_x < self.renderer.width and 0 <= draw_y < self.renderer.height:
                    self.renderer.draw_on_layer(
                        renderable.layer, draw_x, draw_y, tile_id, color=color
                    )

    def _draw_map(
        self, tile_viewport: game.utils.geometry.Rect, player_pos: game.utils.geometry.Point
    ) -> None:
        self.renderer.clear_layer(game.types.RenderLayer.floor)
        self.renderer.clear_layer(game.types.RenderLayer.wall)
        map_x1: int = player_pos.x - tile_viewport.center.x + 1
        map_y1: int = player_pos.y - tile_viewport.center.y + 1
        map_x = map_x1 - 1
        for tile_x in range(tile_viewport.x1, tile_viewport.x2 + 1):
            map_x += 1
            if map_x >= self.world.map.width:
                break
            if map_x < 0:
                continue
            map_y = map_y1 - 1
            for tile_y in range(tile_viewport.y1, tile_viewport.y2 + 1):
                map_y += 1
                if map_y >= self.world.map.height:
                    break
                if map_y < 0:
                    continue
                tile_id, tile_type = self.world.map.get_tile(map_y, map_x)
                # TODO: support tile colorization?
                tile_color = "#00FFFFFF"
                if self.world.map.explored[map_y, map_x]:
                    tile_color = "#60FFFFFF"
                if self.world.map.fov[map_y, map_x]:
                    self.world.map.explored[map_y, map_x] = True
                    tile_color = "#FFFFFFFF"
                if tile_color.startswith("#00"):
                    continue

                draw_x = game.render.snap_tile_to_grid_x("world", tile_x)
                draw_y = game.render.snap_tile_to_grid_y("world", tile_y)
                self.renderer.draw_on_layer(
                    _render_layer_from_tile_type(tile_type),
                    draw_x,
                    draw_y,
                    tile_id,
                    color=tile_color,
                )

    def _get_player_render_data(self) -> game.types.PlayerRenderData:
        # TODO: handle more than one player controlled object?
        for ent, components in self.world.get_components(
            game.component.player.Player,
            game.component.render.Renderable,
            game.component.movement.Position,
        ):
            player, renderable, position = components
            category, name = renderable.tile
            player_tile_id = game.render.TileCache.get(category, name)
            return game.types.PlayerRenderData(
                position.x,
                position.y,
                player.fov,
                renderable.layer,
                player_tile_id,
                renderable.tint,
            )
        return game.types.PlayerRenderData(0, 0, 0, game.types.RenderLayer.player, 0, "white")

    def _on_render_entities(self, _event: game.types.Event) -> None:
        self.should_render_entities = True

    def _on_render_map(self, _event: game.types.Event) -> None:
        self.should_render_map = True

    def _on_game_log(self, event: game.types.Event) -> None:
        self.renderer.clear_layer(game.types.RenderLayer.ui_game_message)
        self.renderer.draw_gamelog_on_layer(
            game.types.RenderLayer.ui_game_message,
            game.render.snap_tile_to_grid_x("font", 1),
            self.renderer.height - game.render.snap_tile_to_grid_y("font", 1),
            event["log_component"].lines,
        )

    def _on_game_over(self, event: game.types.Event) -> None:
        """Game shutdown callback."""
        if event.get("shutdown"):
            log.info("Closing terminal window.")
            self.renderer.close()


def _render_layer_from_tile_type(tile_type: game.types.TileType) -> game.types.RenderLayer:
    return {
        game.types.TileType.wall_v: game.types.RenderLayer.wall,
        game.types.TileType.wall_h: game.types.RenderLayer.wall,
        game.types.TileType.floor: game.types.RenderLayer.floor,
    }[tile_type]
