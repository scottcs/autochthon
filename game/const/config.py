"""Config data."""
import pathlib

import toml

import game.types

_PATH = pathlib.Path("data/default_config.toml")

with _PATH.open() as config_file_handle:
    DATA: game.types.Config = toml.load(config_file_handle)
