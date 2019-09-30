"""Start the game."""
import logging

import game.main

logging.basicConfig(level=logging.ERROR)


if __name__ == "__main__":
    game.main.run()
