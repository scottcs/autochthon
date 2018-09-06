"""Local (non-server) game."""
from typing import Mapping

from game.events import GameOverEvent
from game.core.main import Game
from game.processor.render import TCODRenderProcessor


def run_local(config: Mapping) -> None:
    """Run the game locally."""
    game = Game(TCODRenderProcessor(config['title'],
                                    width=config['local']['width'],
                                    height=config['local']['height']))
    game_loop(game)


def game_loop(game: Game) -> None:
    """Main game loop."""
    while not game.game_over:
        game.update()
        GameOverEvent({'shutdown': True})
