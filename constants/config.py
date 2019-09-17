"""Config data."""
import json
import pathlib
import typing

CONFIG_FILE = pathlib.Path("data/config.json")

with CONFIG_FILE.open() as config_file_handle:
    CONFIG: typing.Dict[typing.Any, typing.Any] = json.load(config_file_handle)
