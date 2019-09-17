"""Loaded tile ids."""
import json
import pathlib
import typing

import game.const.config

_PATH = pathlib.Path(f"data/tiles/{game.const.config.DATA['tiles']['tileset']}/tile_ids.json")

with _PATH.open() as tile_ids_file_handle:
    DATA: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = json.load(tile_ids_file_handle)
