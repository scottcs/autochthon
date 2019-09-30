"""Game log scroll-back state."""
import typing

import game.data
import game.processor.gamelog
import game.render
import game.state.base
import game.types
import game.ui.frame


class GameLog(game.state.base.BaseState):
    """Game log scroll-back state."""

    border = 4

    def __init__(self, renderer: game.render.BaseRenderer) -> None:
        super().__init__()
        self.renderer: game.render.BaseRenderer = renderer
        self.lines: typing.List[game.types.LogLine] = []
        self.line_height: int = 0
        self.num_lines: int = 0

    def on_enter(self):
        """Called when this state is entered."""
        self.line_height = game.data.tileset["font"]["size"][1]
        for log_component in game.processor.gamelog.buffer:
            self.lines.append(log_component.lines)
        self.num_lines = self.renderer.height // self.line_height
        # TODO: finish this
        # self.panel = game.ui.frame.Frame(
        #     4, 4, self.renderer.width - 4, self.renderer.height - 4,
        #
        #           )
        # if not self.panel:
        #     self.panel = game.ui.frame.Frame(
        #         4, 4, self.renderer.width - 4, self.renderer.height - 4
        #     )

    def update(self):
        """Update the game log menu."""
