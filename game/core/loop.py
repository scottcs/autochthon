"""Game loop."""
import game.core.main
import game.events


def run() -> None:
    """Run the game."""
    game_object = game.core.main.Game()
    while not game_object.game_over:
        game_object.update()
