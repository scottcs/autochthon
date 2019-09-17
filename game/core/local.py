"""Local (non-server) game."""
import bearlibterminal.terminal as blt

import game.core.main
import game.events
import game.processor.player_input
import game.processor.render
import gamedata.config


def run_local() -> None:
    """Run the game locally."""
    local_game = game.core.main.Game(gamedata.config.CONFIG)
    game_loop(local_game)


def game_loop(game_object: game.core.main.Game) -> None:
    """Main game loop."""
    while not game_object.game_over:
        game_object.update()
        if blt.has_input():
            game.events.Input.fire()
