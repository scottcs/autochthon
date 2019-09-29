"""Main game class."""
import logging

import game.state.base
import game.state.playing
import game.types

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def _safe_dir(name: str) -> str:
    return name.lower().replace(" ", "_")


class Game:
    """Main game object."""

    def __init__(self) -> None:
        self.game_over: bool = False

        # TODO: menu state first
        # TODO: allow player to set seed and pass it here
        game.state.base.Stack.push(game.state.playing.Playing("Test1"))

    def update(self):
        """Game update."""
        game.state.base.Stack.current.update()

    def _on_game_over(self, event: game.types.Event) -> None:
        if event.get("shutdown"):
            log.info("Shutting down.")
            self.game_over = True
