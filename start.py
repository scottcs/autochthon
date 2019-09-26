"""Start the game."""
import logging

import game.loop

logging.basicConfig(level=logging.ERROR)


if __name__ == "__main__":
    game.loop.run()
