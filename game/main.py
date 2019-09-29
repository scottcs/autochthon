"""Main game class."""
import logging

import game.events
import game.input
import game.state.base
import game.state.playing
import game.types

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class App:
    """Main game object."""

    def __init__(self, input_handler: game.input.InputHandler) -> None:
        self.input_handler = input_handler
        self.shutting_down: bool = False
        game.events.ShutDown.handle(self._on_shutdown)

        # TODO: menu state first
        # TODO: allow player to set seed and pass it here
        game.state.base.Stack.push(game.state.playing.Playing("Test1"))

    def update(self):
        """Game update."""
        if not self.shutting_down:
            self.input_handler.process()
            try:
                game.state.base.Stack.current.update()
            except game.state.base.EmptyStateQueueException:
                log.debug("No current state; initiating shutdown")
                game.events.ShutDown.fire()

    def _on_shutdown(self, _event: game.types.Event) -> None:
        log.info("Shutting down.")
        self.shutting_down = True


def run() -> None:
    """Run the game."""
    app = App(game.input.BearLibInput())
    while not app.shutting_down:
        app.update()
