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

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process all renderables."""
        elapsed = time.time_ns() - self.last_process_time
        if elapsed >= ANIM_FRAME_TIME:
            self.last_process_time = time.time_ns()
            self.anim_tick = (self.anim_tick + 1) % MAX_ANIM_FRAMES
            self.should_render_entities = True

        refresh = False
        player_data = self._get_player_render_data()
        viewport_x = game.render.to_grid_x("monsters", player_data.x) - self.renderer.center[0]
        viewport_y = game.render.to_grid_y("monsters", player_data.y) - self.renderer.center[1]

        self._update_fov(player_data)

        if self.should_render_map:
            self._draw_map(viewport_x, viewport_y)
            self.should_render_map = False
            refresh = True
        if self.should_render_entities:
            self._draw_entities(viewport_x, viewport_y)
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

    def _draw_entities(self, viewport_x: int, viewport_y: int) -> None:
        self.renderer.clear_layer(game.types.RenderLayer.enemy)
        self.renderer.clear_layer(game.types.RenderLayer.item)
        self.renderer.clear_layer(game.types.RenderLayer.player)

        for ent, components in self.world.get_components(
            game.component.render.Renderable, game.component.movement.Position
        ):
            renderable, position = components

            is_dead = self.world.has_component(ent, game.component.status.TMPDead)
            is_contained = self.world.has_component(ent, game.component.container.TMPContained)
            if is_dead or is_contained:
                continue

            pos_x: typing.Optional[int] = None
            pos_y: typing.Optional[int] = None
            facing: typing.Optional[str] = None
            can_see_now: bool = False
            can_see_prev: bool = False
            seen: bool = False

            if position is not None:
                pos_x = position.x
                pos_y = position.y
                facing = position.facing
                can_see_now = self.world.map.fov[position.y, position.x]

            color = "#00FFFFFF"
            if renderable.last_seen_x is not None:
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
                pos_y = renderable.last_seen_y
                pos_x = renderable.last_seen_x
                facing = renderable.last_seen_facing
            # else don't draw it
            else:
                continue

            category, name = renderable.tile
            tile_id = game.render.TileCache.get(
                category, name, direction=facing, frame=self.anim_tick
            )
            if pos_x is not None and pos_y is not None:
                self.renderer.draw_on_layer(
                    renderable.layer,
                    game.render.to_grid_x(category, pos_x) - viewport_x,
                    game.render.to_grid_y(category, pos_y) - viewport_y,
                    tile_id,
                    color=color,
                )

    def _draw_map(self, viewport_x: int, viewport_y: int) -> None:
        self.renderer.clear_layer(game.types.RenderLayer.floor)
        self.renderer.clear_layer(game.types.RenderLayer.wall)
        for tile_x in range(game.render.from_grid_x("world", self.renderer.width)):
            draw_x: int = game.render.to_grid_x("world", tile_x)
            map_x: int = game.render.from_grid_x("world", draw_x + viewport_x)
            if map_x >= self.world.map.width:
                break
            if map_x < 0:
                continue
            for tile_y in range(game.render.from_grid_y("world", self.renderer.height)):
                draw_y: int = game.render.to_grid_y("world", tile_y)
                map_y: int = game.render.from_grid_y("world", draw_y + viewport_y)
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
            game.render.to_grid_x("font", 1),
            self.renderer.height - game.render.to_grid_y("font", 1),
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
