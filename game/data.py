"""Config data."""
import json
import pathlib

import appdirs
import toml

import game.types
import game.utils.dataloader

DEFAULT_CONFIG_PATH = pathlib.Path("data/default_config.toml")

with DEFAULT_CONFIG_PATH.open() as config_file:
    config: game.types.ImportedData = toml.load(config_file)

TILES_PATH = pathlib.Path(f"data/tiles/{config['tileset']}")
TILESET_PATH = pathlib.Path(f"data/tileset/{config['tileset']}")
TILESET_JSON_PATH = pathlib.Path(f"{TILESET_PATH}/tileset.json")
TILE_IDS_JSON_PATH = pathlib.Path(f"{TILESET_PATH}/tile_ids.json")
FONT_PATH = pathlib.Path(f"data/font")

with TILESET_JSON_PATH.open() as tileset_file:
    tileset: game.types.ImportedData = json.load(tileset_file)

with TILE_IDS_JSON_PATH.open() as tile_ids_file:
    tile_ids: game.types.ImportedData = json.load(tile_ids_file)

KEYBINDINGS_PATH = pathlib.Path("data/keybindings.toml")

with KEYBINDINGS_PATH.open() as keybindings_file:
    keybindings: game.types.ImportedData = toml.load(keybindings_file)

VERSION_STRING = f'* {config["title"]} version {game.VERSION}'


def _safe_dir(name: str) -> str:
    return name.lower().replace(" ", "_")


DIRS = appdirs.AppDirs(_safe_dir(config["title"]), _safe_dir(config["org"]))

LOADER: game.utils.dataloader.DataLoader = game.utils.dataloader.DataLoader()
LOADER.load_all_json()
