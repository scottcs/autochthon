"""Config data."""
import json
import pathlib
import typing

_PATH = pathlib.Path("data/config.json")

with _PATH.open() as config_file_handle:
    DATA: typing.Dict[typing.Any, typing.Any] = json.load(config_file_handle)
