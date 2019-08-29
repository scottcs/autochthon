"""Config data."""
import json
from pathlib import Path
from typing import Any, Dict

CONFIG_FILE = Path("data/config.json")

with CONFIG_FILE.open() as config_file_handle:
    CONFIG: Dict[Any, Any] = json.load(config_file_handle)
