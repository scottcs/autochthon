"""Game loop."""
import bearlibterminal.terminal as blt

import game.core.main
import game.events


def run() -> None:
    """Run the game."""
    game_object = game.core.main.Game()
    while not game_object.game_over:
        game_object.update()
        if blt.has_input():
            game.events.Input.fire()
