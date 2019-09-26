"""Tile IDs."""
import json
import pathlib
import typing

import game.tileset

_PATH = pathlib.Path(f"{game.tileset.TILESET_PATH}/tile_ids.json")

with _PATH.open() as f:
    DATA: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = json.load(f)
