"""Loaded tile ids."""
import json
from pathlib import Path

TILE_IDS_FILE = Path('static/img/oryx_ur/tile_ids.json')

with TILE_IDS_FILE.open() as tile_ids_file_handle:
    TILE_IDS = json.load(tile_ids_file_handle)
