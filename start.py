"""Start the game."""
import argparse

from game.server import run_server


def run_local_game():
    """Run the game locally in a tdl window."""
    print('tdl')


def run_game(args: argparse.Namespace):
    """Run the game."""
    if args.local:
        run_local_game()
    else:
        run_server(port=args.port)


def parse_command_line() -> argparse.Namespace:
    """Parse command-line."""
    parser = argparse.ArgumentParser(description='run the game')
    parser.add_argument('-l', '--local',
                        action='store_true',
                        help='run in local window instead of web server')
    parser.add_argument('-P', '--port',
                        action='store',
                        default=None,
                        help='listen port for server')
    return parser.parse_args()


if __name__ == '__main__':
    run_game(parse_command_line())
