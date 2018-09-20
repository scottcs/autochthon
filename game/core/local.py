"""Local (non-server) game."""
from game.events import GameOverEvent
from game.core.main import Game
from game.processor.render import TCODRenderProcessor
from gamedata.config import CONFIG


def run_local() -> None:
    """Run the game locally."""
    game = Game(
        TCODRenderProcessor(
            CONFIG["title"], width=CONFIG["local"]["width"], height=CONFIG["local"]["height"]
        )
    )
    game_loop(game)


def game_loop(game: Game) -> None:
    """Main game loop."""
    while not game.game_over:
        game.update()
        GameOverEvent({"shutdown": True})
