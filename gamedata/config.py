"""Config data."""
import json
from pathlib import Path

CONFIG_FILE = Path("data/config.json")

with CONFIG_FILE.open() as config_file_handle:
    CONFIG: dict = json.load(config_file_handle)
