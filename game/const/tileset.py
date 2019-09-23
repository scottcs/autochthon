"""Loaded tilesets."""
import json
import pathlib
import typing

import game.const.config

TILES_PATH = pathlib.Path(f"data/tiles/{game.const.config.DATA['tileset']}")
TILESET_PATH = pathlib.Path(f"data/tileset/{game.const.config.DATA['tileset']}")
FONT_PATH = pathlib.Path(f"data/font")
_PATH = pathlib.Path(f"{TILESET_PATH}/tileset.json")

with _PATH.open() as f:
    DATA: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = json.load(f)
