"""Draw a UI Frame."""
import logging
import typing

import game.render
import game.ui.widget

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Frame(game.ui.widget.Widget):
    """Generic UI Frame."""

    def __init__(self, *args, style: typing.Optional[str] = None) -> None:
        super().__init__(*args)
        self.style: typing.Optional[str] = style

    def _paint(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        if self.style is not None:
            self._paint_background(renderer, layer)
            self._paint_foreground(renderer, layer + 1)
        else:
            self._paint_foreground(renderer, layer)

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
        return game.render.TileCache.get("interface", self.style, direction=direction)

    def _paint_background(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        renderer.clear_layer(layer, rect=self.rect)
        spacing_x, spacing_y = renderer.spacing["interface"]
        w = self.rect.w // spacing_x
        h = self.rect.h // spacing_y
        for x in range(w):
            for y in range(h):
                tile_id = self._get_style_tile_id(x, y, w - 1, h - 1)
                renderer.draw_on_layer(
                    layer, self.rect.x1 + (x * spacing_x), self.rect.y1 + (y * spacing_y), tile_id
                )

    def _paint_foreground(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        renderer.clear_layer(layer, rect=self.rect)
        renderer.draw_text_on_layer(layer, self.rect.x1 + 1, self.rect.y1 + 1, "TEST")
