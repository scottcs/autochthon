"""Loaded tile ids."""
import pathlib

import toml

import game.const.config
import game.types

BASE_PATH = pathlib.Path(f"data/tiles/{game.const.config.DATA['tiles']['tileset']}")
_PATH = pathlib.Path(f"{BASE_PATH}/tileset.toml")

with _PATH.open() as tile_ids_file_handle:
    DATA: game.types.TilesetData = toml.load(tile_ids_file_handle)
