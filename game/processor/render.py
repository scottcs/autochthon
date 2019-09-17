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

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class BearLibRender(esper.Processor):
    """Game render processor for BearLibTerminal console."""

    def __init__(self) -> None:
        self.render_entities: set = set()
        game.events.GameOver.handle(self._on_game_over)

        if not blt.open():
            log.critical("Unable to initialize terminal window!")

        window_data = game.const.tileset.DATA["window"]
        window_size = f"size={window_data['width']}x{window_data['height']}"
        cell_data = game.const.tileset.DATA["cell"]
        cell_size = f"cellsize={cell_data['width']}x{cell_data['height']}"
        title = game.const.config.DATA["title"]
        blt.set(f"window: {window_size}, {cell_size}, resizable=true, title='{title}'")
        self._load_tilesets()
        blt.put(0, 0, game.const.tile_ids.DATA["monsters"]["hero_fighter"]["e"][0])
        blt.put(
            window_data["width"] - 1,
            0,
            game.const.tile_ids.DATA["monsters"]["hero_barbarian"]["w"][0],
        )
        blt.put(
            0,
            window_data["height"] - 1,
            game.const.tile_ids.DATA["monsters"]["hero_thief"]["n"][0],
        )
        blt.put(
            window_data["width"] - 1,
            window_data["height"] - 1,
            game.const.tile_ids.DATA["monsters"]["hero_crusader"]["s"][0],
        )

    def _load_tilesets(self) -> None:
        for item in game.const.tileset.DATA["tilesets"].values():
            item_file = pathlib.Path(f"{game.const.tileset.TILES_PATH}/{item['file']}")
            blt.set(f"{item['offset']}: {item_file}, size={item['size']}")

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process all renderables."""

        # PLAYER POSITION
        # for ent, components in self.world.get_components(
        #     game.component.player.Player,
        #     game.component.render.Renderable,
        #     game.component.movement.Position,
        # ):
        #     position = components[-1]
        #     player_x = position.x
        #     player_y = position.y
        #     fov = components[0].fov
        #     # TODO: handle more than one player controlled object?
        #     break

        blt.refresh()

    def _on_game_over(self, event: game.types.Event):
        """Game shutdown callback."""
        if event.get("shutdown"):
            log.info("Closing terminal window.")
            blt.close()
