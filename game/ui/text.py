"""Text widget."""
import game.render
import game.ui.widget
import game.utils.geometry


class Text(game.ui.widget.Widget):
    """Text widget."""

    def __init__(self, text: str) -> None:
        grid_w = game.render.snap_tile_to_grid_x("font", len(text))
        grid_h = game.render.snap_tile_to_grid_y("font", 1)
        super().__init__(game.utils.geometry.Rect(0, 0, grid_w, grid_h))
        self.text = text

    def _paint(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        renderer.draw_text_on_layer(layer, self.rect.x1, self.rect.y1, self.text)
