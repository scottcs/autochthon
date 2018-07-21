"""Start the game."""
import argparse

import toml

from game.local import run_local
from game.server import run_server


def run_game(args: argparse.Namespace):
    """Run the game."""
    with open(args.config) as f:
        config = toml.load(f)
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
                        default='config.toml',
                        help='configuration TOML file')
    return parser.parse_args()


if __name__ == '__main__':
    run_game(parse_command_line())
