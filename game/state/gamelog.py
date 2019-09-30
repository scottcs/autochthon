"""Game log scroll-back state."""
import game.state.base
import game.types


class GameLog(game.state.base.BaseState):
    """Game log scroll-back state."""

    def __init__(self) -> None:
        super().__init__()
        self.input_handler = GameLogInput()

    def on_enter(self) -> None:
        """Called when this state is entered."""


class GameLogInput(game.state.base.StateInput):
    """Game log scroll-back input handler."""

    def handle(self, input_key: game.types.InputKey) -> None:
        """Handle input."""
        # TODO: scroll up and down and quit
        pass
