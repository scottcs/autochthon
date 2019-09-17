"""Loaded tile ids."""
import json
import pathlib
import typing

import constants.config

TILE_IDS_FILE = pathlib.Path(
    f"data/tiles/{constants.config.CONFIG['tiles']['tileset']}/tile_ids.json"
)

with TILE_IDS_FILE.open() as tile_ids_file_handle:
    TILE_IDS: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = json.load(
        tile_ids_file_handle
    )
