"""Morgue utilities."""
import logging
import pathlib
import time

import game.data


def new() -> logging.Logger:
    """Set up the morgue log."""
    morgue_dir = (
        pathlib.Path(game.data.DIRS.user_log_dir)
        / pathlib.Path(game.data.config["directories"]["base"])
        / pathlib.Path(game.data.config["directories"]["morgue"])
        / pathlib.Path(game.data.config["player"]["name"])
    )
    morgue_dir.mkdir(parents=True, exist_ok=True)
    log_file = morgue_dir / pathlib.Path(f"{time.time()}.morgue")
    handler = logging.FileHandler(str(log_file))
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(message)s"))
    morgue_log = logging.getLogger("morgue")
    morgue_log.setLevel(logging.INFO)
    for old_handler in morgue_log.handlers[:]:
        morgue_log.removeHandler(old_handler)
    morgue_log.addHandler(handler)
    morgue_log.propagate = False
    return morgue_log
