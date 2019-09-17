"""Game loop."""
import bearlibterminal.terminal as blt

import game.constants.config
import game.core.main
import game.events
import game.processor.player_input
import game.processor.render


def run() -> None:
    """Run the game."""
    game_object = game.core.main.Game(game.constants.config.DATA)
    while not game_object.game_over:
        game_object.update()
        if blt.has_input():
            game.events.Input.fire()
