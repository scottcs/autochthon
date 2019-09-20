"""Render processors."""
import logging
import pathlib
import typing

import bearlibterminal.terminal as blt
import esper

import game.component.movement
import game.component.player
import game.component.render
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
        self.render_entities: set = set()
        self.width = game.const.tileset.DATA["window"]["width"]
        self.height = game.const.tileset.DATA["window"]["height"]

        game.events.GameOver.handle(self._on_game_over)

        if not blt.open():
            log.critical("Unable to initialize terminal window!")

        window_size = f"size={self.width}x{self.height}"

        cell_data = game.const.tileset.DATA["cell"]
        cell_size = f"cellsize={cell_data['width']}x{cell_data['height']}"
        title = game.const.config.DATA["title"]
        blt.set(f"window: {window_size}, {cell_size}, resizable=true, title='{title}'")
        self._load_tilesets()

    @staticmethod
    def _load_tilesets() -> None:
        for item in game.const.tileset.DATA["tilesets"].values():
            item_file = pathlib.Path(f"{game.const.tileset.TILES_PATH}/{item['file']}")
            load_str = f"{item['offset']}: {item_file}, size={item['size']}"
            if "align" in item:
                load_str += f", align={item['align']}"
            blt.set(load_str)

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process all renderables."""
        blt.layer(game.types.RenderLayer.background)
        blt.color("white")

        player_data = self._get_player_render_data()
        center_x = self.width // 2
        center_y = self.height // 2
        viewport_x = player_data.x - center_x
        viewport_y = player_data.y - center_y

        # TODO: fov
        # TODO: enemies
        # TODO: items
        # TODO: optimize

        for draw_x in range(self.width):
            map_x: int = draw_x + viewport_x
            if map_x >= self.world.map.width:
                break
            if map_x < 0:
                continue
            for draw_y in range(self.height):
                map_y: int = draw_y + viewport_y
                if map_y >= self.world.map.height:
                    break
                if map_y < 0:
                    continue
                tile_id, tile_type = self.world.map.get_tile(map_y, map_x)
                blt.layer(_render_layer_from_tile_type(tile_type))
                blt.put(draw_x, draw_y, tile_id)

        blt.layer(player_data.layer)
        blt.color(player_data.color)
        blt.put(center_x, center_y, player_data.tile_id)

        blt.refresh()

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

    @staticmethod
    def _on_game_over(event: game.types.Event):
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
