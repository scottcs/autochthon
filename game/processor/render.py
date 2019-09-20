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
import game.const.tile_ids
import game.const.tileset
import game.events
import game.types
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

        # PLAYER POSITION
        player_x: int = 0
        player_y: int = 0
        # fov: int = 0
        player_tile_id: int = 0
        for ent, components in self.world.get_components(
            game.component.player.Player,
            game.component.render.Renderable,
            game.component.movement.Position,
        ):
            player, renderable, position = components
            player_x = position.x
            player_y = position.y
            category, name = renderable.tile_id
            player_tile_id = game.utils.render.TileCache.get(category, name, frame=1)
            # fov = player.fov
            # TODO: handle more than one player controlled object?
            break

        center_x = self.width // 2
        center_y = self.height // 2
        viewport_x1 = max(0, player_x - center_x)
        viewport_x2 = min(self.width, player_x + center_x)
        viewport_y1 = max(0, player_y - center_y)
        viewport_y2 = min(self.height, player_y + center_y)
        blt.put(center_x, center_y, player_tile_id)

        for map_x in range(viewport_x1, viewport_x2):
            for map_y in range(viewport_y1, viewport_y2):
                # TODO: draw
                pass

        blt.refresh()

    @staticmethod
    def _on_game_over(event: game.types.Event):
        """Game shutdown callback."""
        if event.get("shutdown"):
            log.info("Closing terminal window.")
            blt.close()
