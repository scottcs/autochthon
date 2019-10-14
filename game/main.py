"""Main game class."""
import logging

import pprofile

import game.data
import game.events
import game.input
import game.render
import game.state.base
import game.state.playing
import game.types

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class App:
    """Main game object."""

    def __init__(
        self, renderer: game.render.BaseRenderer, input_handler: game.input.InputHandler
    ) -> None:
        self.renderer = renderer
        self.input_handler = input_handler
        self.shutting_down: bool = False
        game.events.ShutDown.handle(self._on_shutdown)
        log.info(game.data.VERSION_STRING)

        # TODO: menu state first
        # TODO: allow player to set seed and pass it here
        game.state.base.Stack.push(game.state.playing.Playing(self.renderer, "Test1"))

    def update(self):
        """Game update."""
        if not self.shutting_down:
            self.input_handler.process()
            try:
                game.state.base.Stack.current.update()
            except game.state.base.EmptyStateQueueException:
                log.debug("No current state; initiating shutdown")
                game.events.ShutDown()

    def _on_shutdown(self, _event: game.types.Event) -> None:
        log.info("Shutting down.")
        self.shutting_down = True


def run() -> None:
    """Run the game."""
    app = App(game.render.BearLibRenderer(), game.input.BearLibInput())
    while not app.shutting_down:
        app.update()


def run_with_profiler() -> None:
    """Run the game with a deterministic profiler."""
    app = App(game.render.BearLibRenderer(), game.input.BearLibInput())
    profiler = pprofile.Profile()
    with profiler:
        while not app.shutting_down:
            app.update()
    profiler.dump_stats("cachegrind.out.prof")


def run_with_statistic_profiler() -> None:
    """Run the game with a statistic profiler."""
    app = App(game.render.BearLibRenderer(), game.input.BearLibInput())
    profiler = pprofile.StatisticalProfile()
    # period = 1ms, only sample current thread
    with profiler(period=0.001, single=True):
        while not app.shutting_down:
            app.update()
    profiler.dump_stats("cachegrind.out.prof")
