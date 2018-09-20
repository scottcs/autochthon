"""Start the game."""
import argparse
import logging

from game.core.local import run_local
from game.core.server import run_server
from gamedata.config import CONFIG_FILE

logging.basicConfig(level=logging.ERROR)


def run_game(args: argparse.Namespace) -> None:
    """Run the game."""
    if args.local:
        run_local()
    else:
        run_server()


def parse_command_line() -> argparse.Namespace:
    """Parse command-line."""
    parser = argparse.ArgumentParser(description='run the game')
    parser.add_argument('-l', '--local',
                        action='store_true',
                        help='run in local window instead of web server')
    parser.add_argument('-c', '--config',
                        action='store',
                        default=CONFIG_FILE,
                        help='configuration JSON file')
    return parser.parse_args()


if __name__ == '__main__':
    run_game(parse_command_line())
