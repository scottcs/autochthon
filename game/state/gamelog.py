"""Game log scroll-back state."""
import logging
import typing

import game.data
import game.input
import game.processor.gamelog
import game.render
import game.state.base
import game.types
import game.ui.frame
import game.ui.text
import game.ui.widget
import game.utils.geometry

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GameLog(game.state.base.BaseState):
    """Game log scroll-back state."""

    border = 4

    def __init__(self, renderer: game.render.BaseRenderer) -> None:
        self.renderer = renderer
        self.lines: typing.List[game.types.LogLine] = []
        self.num_lines = 0
        self.frame: typing.Optional[game.ui.frame.Frame] = None
        self.do_render = False

    def _on_enter(self):
        """Called when this state is entered."""
        outer_margin = 8
        inner_margin = 2
        for log_component in game.processor.gamelog.buffer:
            self.lines.append(log_component.lines)
        inner_height = self.renderer.height - (outer_margin * 2) - (inner_margin * 2)
        self.num_lines = min(len(self.lines), inner_height)
        self.frame = game.ui.frame.Frame(
            game.utils.geometry.Rect(
                outer_margin,
                outer_margin,
                self.renderer.width - (outer_margin * 2),
                self.renderer.height - (outer_margin * 2),
            ),
            style=game.types.UIFrameStyle.stone,
        )
        for y in range(self.num_lines):
            self.frame.add_widget(game.ui.text.Text(self.renderer.colorize_gamelog(self.lines[y])))
        self.frame.set_layout(game.ui.widget.VerticalLayout(inner_margin, 0))
        self.frame.show()
        self.do_render = True

    def _on_exit(self):
        """Called when this state is dropped."""
        self.frame.hide()
        self.renderer.clear_layer(game.types.RenderLayer.ui)

    def _update(self):
        """Update the game log menu."""
        if self.do_render:
            self.do_render = False
            self.frame.render(self.renderer)
            self.renderer.refresh()

    def _on_input(self, event: game.types.Event) -> None:
        input_key = event["key"]
        if game.input.GameInterface.match("quit", input_key):
            game.state.base.Stack.pop_to(self)
