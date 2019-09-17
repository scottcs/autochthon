"""Loaded tile ids."""
import json
import pathlib
import typing

TILE_IDS_FILE = pathlib.Path("data/tiles/oryx_ur/tile_ids.json")

with TILE_IDS_FILE.open() as tile_ids_file_handle:
    TILE_IDS: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = json.load(
        tile_ids_file_handle
    )
