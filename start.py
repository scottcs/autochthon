"""Start the game."""
import argparse
import json
import logging
from pathlib import Path

from game.local import run_local
from game.server import run_server

CONFIG_FILE = Path('data') / Path('config.json')

logging.basicConfig(level=logging.ERROR)


def run_game(args: argparse.Namespace) -> None:
    """Run the game."""
    with open(args.config) as f:
        config = json.load(f)
    if args.local:
        run_local(config)
    else:
        run_server(config)


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
