"""Render processors."""
import logging
import pathlib
import typing

import bearlibterminal.terminal as blt
import esper
import tcod

import game.component.container
import game.component.movement
import game.component.player
import game.component.render
import game.component.status
import game.const.config
import game.const.palette
import game.const.tile_ids
import game.const.tileset
import game.events
import game.types
import game.utils.geometry
import game.utils.render

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class BearLibRender(esper.Processor):
    """Game render processor for BearLibTerminal console."""

    def __init__(self) -> None:
        self.width: int = game.const.tileset.DATA["window"]["width"]
        self.height: int = game.const.tileset.DATA["window"]["height"]
        self.center: typing.List[int] = [self.width // 2, self.height // 2]
        self.spacing: typing.Dict[str, typing.List[int]] = {}
        self.should_render_map: bool = True
        self.should_render_entities: bool = True
        self.known_player_xy: typing.List[int] = [-1, -1]

        game.events.RenderEntities.handle(self._on_render_entities)
        game.events.RenderMap.handle(self._on_render_map)
        game.events.GameLog.handle(self._on_game_log)
        game.events.GameOver.handle(self._on_game_over)

        if not blt.open():
            log.critical("Unable to initialize terminal window!")

        window_size = f"size={self.width}x{self.height}"
        font_data = game.const.tileset.DATA["font"]
        font_file = pathlib.Path(f"{game.const.tileset.FONT_PATH}/{font_data['file']}")

        title = game.const.config.DATA["title"]
        blt.set(f"window: {window_size}, resizable=true, title='{title}'")
        blt.set(f"font: {font_file}, size={str(font_data['size'][0])}x{str(font_data['size'][1])}")
        blt.color("white")
        self._load_tilesets()

    def _load_tilesets(self) -> None:
        tile_scale = game.const.config.DATA.get("tile_scale", 1)
        for tileset_name, item in game.const.tileset.DATA["tilesets"].items():
            item_file = pathlib.Path(f"{game.const.tileset.TILES_PATH}/{item['file']}")
            load_str = f"{item['offset']}: {item_file}"
            if "size" in item:
                width, height = item["size"]
                load_str += f", size={str(width)}x{str(height)}"
                if tile_scale != 1:
                    width *= tile_scale
                    height *= tile_scale
                    load_str += f", resize={str(width)}x{str(height)}, resize-filter=nearest"
            if "align" in item:
                load_str += f", align={item['align']}"
            if "spacing" in item:
                x, y = item["spacing"]
                if tile_scale != 1:
                    x *= tile_scale
                    y *= tile_scale
                load_str += f", spacing={str(x)}x{str(y)}"
                self.spacing[tileset_name] = [x, y]
            else:
                self.spacing[tileset_name] = game.const.tileset.DATA["font"]["spacing"]
            blt.set(load_str)

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process all renderables."""
        refresh = False
        player_data = self._get_player_render_data()
        viewport_x = (player_data.x * self.spacing["monsters"][0]) - self.center[0]
        viewport_y = (player_data.y * self.spacing["monsters"][1]) - self.center[1]

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
            blt.refresh()

    def _clear_layer(self, layer: game.types.RenderLayer):
        current_layer = blt.state(blt.TK_LAYER)
        blt.layer(layer)
        blt.clear_area(0, 0, self.width, self.height)
        blt.layer(current_layer)

    @staticmethod
    def _draw_on_layer(
        layer: game.types.RenderLayer,
        x: int,
        y: int,
        tile_id: int,
        color: typing.Optional[str] = None,
    ):
        current_layer = blt.state(blt.TK_LAYER)
        current_color = blt.state(blt.TK_COLOR)
        blt.layer(layer)
        if color is not None:
            blt.color(color)
        blt.put(x, y, tile_id)
        blt.layer(current_layer)
        blt.color(current_color)

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

    def _draw_entities(self, viewport_x, viewport_y):
        self._clear_layer(game.types.RenderLayer.enemy)
        self._clear_layer(game.types.RenderLayer.item)
        self._clear_layer(game.types.RenderLayer.player)

        for ent, components in self.world.get_components(
            game.component.render.Renderable, game.component.movement.Position
        ):
            renderable, position = components
            # is_dead = self.world.has_component(ent, game.component.status.TMPDead)
            # is_contained = self.world.has_component(ent, game.component.container.TMPContained)
            pos_x = pos_y = None
            can_see_now = can_see_prev = seen = False

            if position is not None:
                pos_x = position.x
                pos_y = position.y
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
            # else if we can see where it last was, forget where we've seen it and don't draw it
            elif can_see_prev:
                renderable.last_seen_y = None
                renderable.last_seen_x = None
            # else if we've seen it, draw it faded where we last saw it
            elif seen:
                color = "#60FFFFFF"
                pos_y = renderable.last_seen_y
                pos_x = renderable.last_seen_x
            # else don't draw it
            else:
                continue
            category, name = renderable.tile_id
            tile_id = game.utils.render.TileCache.get(category, name)
            self._draw_on_layer(
                renderable.layer,
                (pos_x * self.spacing["monsters"][0]) - viewport_x,
                (pos_y * self.spacing["monsters"][1]) - viewport_y,
                tile_id,
                color=color,
            )

    def _draw_map(self, viewport_x, viewport_y):
        self._clear_layer(game.types.RenderLayer.floor)
        self._clear_layer(game.types.RenderLayer.wall)
        spacing_x, spacing_y = self.spacing["world"]

        for draw_x in range(0, self.width, spacing_x):
            x: int = (draw_x + viewport_x) // spacing_x
            if x >= self.world.map.width:
                break
            if x < 0:
                continue
            for draw_y in range(0, self.height, spacing_y):
                y: int = (draw_y + viewport_y) // spacing_y
                if y >= self.world.map.height:
                    break
                if y < 0:
                    continue
                tile_id, tile_type = self.world.map.get_tile(y, x)
                # TODO: support tile colorization?
                tile_color = "#00FFFFFF"
                if self.world.map.explored[y, x]:
                    tile_color = "#60FFFFFF"
                if self.world.map.fov[y, x]:
                    self.world.map.explored[y, x] = True
                    tile_color = "#FFFFFFFF"
                if tile_color.startswith("#00"):
                    continue

                self._draw_on_layer(
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
            category, name = renderable.tile_id
            player_tile_id = game.utils.render.TileCache.get(category, name)
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
        current_layer = blt.state(blt.TK_LAYER)
        blt.layer(game.types.RenderLayer.ui_log)
        blt.clear_area(0, 0, self.width, self.height)
        blt.puts(0, self.height - 2, self._format_game_log(event["lines"], 4, 0))
        blt.layer(current_layer)

    @staticmethod
    def _format_game_log(
        lines: typing.Sequence[game.types.LogLine], offset_x: int, offset_y: int
    ) -> str:
        formatted = f"[offset={offset_x},{offset_y}]"
        for line in lines:
            formatted += f"[color={line.color}]{line.message}[/color]"
        return formatted

    @staticmethod
    def _on_game_over(event: game.types.Event) -> None:
        """Game shutdown callback."""
        if event.get("shutdown"):
            log.info("Closing terminal window.")
            blt.close()


def _render_layer_from_tile_type(tile_type: game.types.TileType) -> game.types.RenderLayer:
    return {
        game.types.TileType.wall_v: game.types.RenderLayer.wall,
        game.types.TileType.wall_h: game.types.RenderLayer.wall,
        game.types.TileType.floor: game.types.RenderLayer.floor,
    }[tile_type]
