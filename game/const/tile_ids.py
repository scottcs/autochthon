"""Tile IDs."""
import json
import pathlib
import typing

import game.const.tileset

_PATH = pathlib.Path(f"{game.const.tileset.TILESET_PATH}/tile_ids.json")

with _PATH.open() as f:
    RAW_DATA: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = json.load(f)

DATA: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = {}
for category, data in RAW_DATA.items():
    main_offset = int(game.const.tileset.DATA["tilesets"][category]["offset"], 0)
    DATA[category] = {}
    for sprite_name, sprite_data in data.items():
        sprite_offset = main_offset + int(sprite_data["offset"])
        adjusted_data = {}
        for direction in ("n", "ne", "e", "se", "s", "sw", "w", "nw"):
            if direction not in sprite_data:
                continue
            adjusted_data[direction] = [sprite_offset + int(x) for x in sprite_data[direction]]
        DATA[category][sprite_name] = adjusted_data
