"""Input utilities."""
import json
from pathlib import Path
from typing import Dict


KEYS_JSON = Path("data") / Path("keys.json")

with open(KEYS_JSON) as f:
    keys_data: dict = json.load(f)
    keys: dict = keys_data["Keys"]
    keys_reverse: dict = {v: k for k, v in keys.items()}
    modifiers: dict = keys_data["Modifiers"]
    events: dict = keys_data["Events"]


def unpack_modifiers(mods: int) -> Dict[str, bool]:
    """Unpack key modifiers from a keyboard event."""
    return {
        "shift": mods & modifiers["Shift"] != 0,
        "ctrl": mods & modifiers["Ctrl"] != 0,
        "alt": mods & modifiers["Alt"] != 0,
    }


def get_key(code: int) -> str:
    """Get a key from a key code."""
    try:
        return str(keys_reverse[code]).lower()
    except KeyError:
        return chr(code).lower()
