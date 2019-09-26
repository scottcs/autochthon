"""Config data."""
import json
import pathlib
import typing

import toml

import game.types

DEFAULT_CONFIG_PATH = pathlib.Path("data/default_config.toml")
with DEFAULT_CONFIG_PATH.open() as config_file_handle:
    config: game.types.Config = toml.load(config_file_handle)

TILES_PATH = pathlib.Path(f"data/tiles/{config['tileset']}")
TILESET_PATH = pathlib.Path(f"data/tileset/{config['tileset']}")
TILESET_JSON_PATH = pathlib.Path(f"{TILESET_PATH}/tileset.json")
TILE_IDS_JSON_PATH = pathlib.Path(f"{TILESET_PATH}/tile_ids.json")
FONT_PATH = pathlib.Path(f"data/font")

with TILESET_JSON_PATH.open() as f:
    tileset: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = json.load(f)

with TILE_IDS_JSON_PATH.open() as f:
    tile_ids: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = json.load(f)
