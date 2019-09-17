"""Start the game."""
import logging

import game.core.local

logging.basicConfig(level=logging.ERROR)


if __name__ == "__main__":
    game.core.local.run_local()
