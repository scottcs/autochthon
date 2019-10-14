"""Scrolling panel."""
import game.render
import game.ui.frame


class ScrollingPanel(game.ui.frame.Frame):
    """A panel that allows scrolling of its content."""

    def _paint(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        super()._paint(renderer, layer)
