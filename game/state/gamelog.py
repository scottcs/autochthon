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
import game.ui.widget
import game.utils.geometry

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GameLog(game.state.base.BaseState):
    """Game log scroll-back state."""

    border = 4

    def __init__(self, renderer: game.render.BaseRenderer) -> None:
        self.renderer: game.render.BaseRenderer = renderer
        self.lines: typing.List[game.types.LogLine] = []
        self.line_height: int = 0
        self.num_lines: int = 0
        self.frame: typing.Optional[game.ui.frame.Frame] = None
        self.do_render: bool = False

    def _on_enter(self):
        """Called when this state is entered."""
        self.line_height = game.data.tileset["font"]["size"][1]
        for log_component in game.processor.gamelog.buffer:
            self.lines.append(log_component.lines)
        self.num_lines = self.renderer.height // self.line_height
        self.frame = game.ui.frame.Frame(
            game.utils.geometry.Rect(10, 10, 80, 20), style="panel_stone_cracked"
        )
        # self.frame.set_layout(game.ui.widget.VerticalLayout(4, 4))
        self.frame.show()
        self.do_render = True

    def _on_exit(self):
        """Called when this state is dropped."""
        self.frame.hide()
        self.renderer.clear_layer(game.types.RenderLayer.ui_low_menu_bg)
        self.renderer.clear_layer(game.types.RenderLayer.ui_low_menu_fg)

    def _update(self):
        """Update the game log menu."""
        if self.do_render:
            self.do_render = False
            self.frame.render(self.renderer, game.types.RenderLayer.ui_low_menu_bg)
            self.renderer.refresh()

    def _on_input(self, event: game.types.Event) -> None:
        input_key = event["key"]
        if game.input.GameInterface.match("quit", input_key):
            game.state.base.Stack.pop_to(self)
