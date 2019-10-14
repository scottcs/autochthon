"""Draw a UI Frame."""
import logging
import typing

import game.render
import game.types
import game.ui.widget
import game.utils.geometry
import game.utils.random

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Frame(game.ui.widget.Widget):
    """Generic UI Frame."""

    def __init__(self, *args, style: typing.Optional[game.types.UIFrameStyle] = None) -> None:
        super().__init__(*args)
        self.style: typing.Optional[game.types.UIFrameStyle] = style
        self._rng = game.utils.random.RNGCache.get("UIFrame")

    def render(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        """Render this widget; OVERRIDES parent."""
        if not self._visible:
            return
        if self.style is not None:
            self._paint(renderer, layer)
        for child in self.children:
            child.render(renderer, layer + 1)

    def _get_style_tile_id(self, x: int, y: int, w: int, h: int):
        if self.style is None:
            return
        direction = "base"
        if x == 0:
            if y == 0:
                direction = "nw"
            elif y == h:
                direction = "sw"
            else:
                direction = "w"
        elif x == w:
            if y == 0:
                direction = "ne"
            elif y == h:
                direction = "se"
            else:
                direction = "e"
        elif y == 0:
            direction = "n"
        elif y == h:
            direction = "s"
        if direction in ("nw", "sw", "ne", "se") or (
            self._rng.percent(0.40)
            and (
                (direction == "w" and (y % 3 == 0))
                or (direction == "e" and (y % 3 == 2))
                or (direction == "n" and (x % 3 == 0))
                or (direction == "s" and (x % 3 == 2))
            )
        ):
            name = {
                game.types.UIFrameStyle.stone: "panel_stone_cracked",
                game.types.UIFrameStyle.scroll: "panel_scroll_worn",
                game.types.UIFrameStyle.window: "panel_window",
                game.types.UIFrameStyle.bubble: "bubble",
            }[self.style]
        else:
            name = {
                game.types.UIFrameStyle.stone: "panel_stone",
                game.types.UIFrameStyle.scroll: "panel_scroll",
                game.types.UIFrameStyle.window: "panel_window",
                game.types.UIFrameStyle.bubble: "bubble",
            }[self.style]
        return game.render.TileCache.get("interface", name, direction=direction)

    def _paint(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        grid_x = self.rect.x1
        grid_y = self.rect.y1
        w = self.rect.w
        h = self.rect.h
        tile_w = game.render.grid_to_tile_x("interface", w)
        tile_h = game.render.grid_to_tile_y("interface", h)
        renderer.clear_layer(layer, rect=game.utils.geometry.Rect(grid_x, grid_y, w, h))
        for tile_x in range(tile_w):
            for tile_y in range(tile_h):
                tile_id = self._get_style_tile_id(tile_x, tile_y, tile_w - 1, tile_h - 1)
                renderer.draw_on_layer(
                    layer,
                    grid_x + game.render.snap_tile_to_grid_x("interface", tile_x),
                    grid_y + game.render.snap_tile_to_grid_y("interface", tile_y),
                    tile_id,
                )
