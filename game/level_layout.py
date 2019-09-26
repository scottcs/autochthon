"""Loaded level layout."""
import json
import pathlib
import typing

_PATH = pathlib.Path("data/layout")
DATA: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = {}

for layout_path in _PATH.glob("*.json"):
    with layout_path.open() as f:
        layout_data = json.load(f)
        for layout in layout_data:
            DATA[layout["name"]] = layout
