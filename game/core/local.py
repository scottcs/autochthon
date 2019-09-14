"""Local (non-server) game."""
import game.core.main
import game.events
import game.processor.render
import gamedata.config


def run_local() -> None:
    """Run the game locally."""
    local_game = game.core.main.Game(
        game.processor.render.TCODRenderProcessor(
            gamedata.config.CONFIG["title"],
            width=gamedata.config.CONFIG["local"]["width"],
            height=gamedata.config.CONFIG["local"]["height"],
        )
    )
    game_loop(local_game)


def game_loop(game_object: game.core.main.Game) -> None:
    """Main game loop."""
    while not game_object.game_over:
        game_object.update()
        game.events.GameOver({"shutdown": True})
