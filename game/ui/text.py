"""Text widget."""
import game.render
import game.ui.widget
import game.utils.geometry


class Text(game.ui.widget.Widget):
    """Text widget."""

    def __init__(self, text: str, offset_x: int = 0, offset_y: int = 0) -> None:
        self.text = text
        self.offset_x = offset_x
        self.offset_y = offset_y
        w = len(self.text)
        h = 1
        super().__init__(game.utils.geometry.Rect(self.offset_x, self.offset_y, w, h))

    def _paint(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        renderer.draw_text_on_layer(layer, self.rect.x1, self.rect.y1, self.text)
