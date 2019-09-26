"""Game loop."""
import game.events
import game.main


def run() -> None:
    """Run the game."""
    game_object = game.main.Game()
    while not game_object.game_over:
        game_object.update()
