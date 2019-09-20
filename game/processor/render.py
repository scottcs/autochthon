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
        # TODO: optimize
        blt.layer(game.types.RenderLayer.background)
        blt.color("white")

        player_data = self._get_player_render_data()
        center_x = self.width // 2
        center_y = self.height // 2
        viewport_x = player_data.x - center_x
        viewport_y = player_data.y - center_y

        self.world.map.compute_fov(
            player_data.x,
            player_data.y,
            algorithm=tcod.FOV_PERMISSIVE_3,
            radius=player_data.fov,
            light_walls=True,
        )

        self._draw_map(viewport_x, viewport_y)
        self._draw_entities(viewport_x, viewport_y)
        self._draw_player(center_x, center_y, player_data)

        blt.refresh()

    @staticmethod
    def _draw_player(center_x, center_y, player_data):
        blt.layer(player_data.layer)
        blt.color(player_data.color)
        blt.put(center_x, center_y, player_data.tile_id)

    def _draw_entities(self, viewport_x, viewport_y):
        render_entities = set()
        for ent, renderable in self.world.get_component(game.component.render.Renderable):
            position = self.world.optional_component_for_entity(
                ent, game.component.movement.Position
            )
            if position is not None:
                if self.world.map.fov[position.y, position.x]:
                    # we can see it now
                    render_entities.add((renderable.layer.value, ent))
            if renderable.last_seen_x is not None:
                # we've seen it before
                render_entities.add((renderable.layer.value, ent))

        for _, ent in sorted(render_entities):
            renderable = self.world.component_for_entity(ent, game.component.render.Renderable)
            position = self.world.optional_component_for_entity(
                ent, game.component.movement.Position
            )
            # is_dead = self.world.has_component(ent, game.component.status.GUTDead)
            # is_contained = self.world.has_component(ent, game.component.container.GUTContained)
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
                renderable.last_seen_y = position.y
                renderable.last_seen_x = position.x
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
            blt.layer(renderable.layer)
            blt.color(color)
            category, name = renderable.tile_id
            tile_id = game.utils.render.TileCache.get(category, name)
            blt.put(pos_x - viewport_x, pos_y - viewport_y, tile_id)

    def _draw_map(self, viewport_x, viewport_y):
        for draw_x in range(self.width):
            x: int = draw_x + viewport_x
            if x >= self.world.map.width:
                break
            if x < 0:
                continue
            for draw_y in range(self.height):
                y: int = draw_y + viewport_y
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

                blt.layer(_render_layer_from_tile_type(tile_type))
                blt.put(draw_x, draw_y, tile_id)

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
