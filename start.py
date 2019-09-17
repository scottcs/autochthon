"""Start the game."""
import logging

import game.core.loop

logging.basicConfig(level=logging.ERROR)


if __name__ == "__main__":
    game.core.loop.run()
