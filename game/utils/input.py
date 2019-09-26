"""Input utilities."""
import logging
import typing

import bearlibterminal.terminal as blt

import game.data
import game.types

log = logging.getLogger(__name__)


def name_to_keycode(name: str) -> typing.Optional[int]:
    """Convert a key by name to a key code."""
    for k, v in blt.__dict__.items():
        if k.startswith("TK_"):
            if k[3:] == name.upper():
                return v
    return None


class KeyMap:
    """Contains mapping of keybindings to input events."""

    def __init__(self, group: str, subgroup: str) -> None:
        self.group = group
        self.subgroup = subgroup
        self.keys: typing.Dict[str, game.types.InputKey] = {}
        self.reload()

    def reload(self) -> None:
        """(Re)load the key mappings from game data."""
        keys: typing.Dict[str, game.types.InputKey] = {}
        for key, key_map in game.data.keybindings[self.group][self.subgroup].items():
            keycode = name_to_keycode(key_map["name"])
            if keycode is None:
                log.error(f"Could not determine keycode for {key_map}")
                continue
            keys[key.lower()] = game.types.InputKey(
                key_map["name"], keycode, key_map["shift"], key_map["ctrl"], key_map["alt"]
            )
        self.keys = keys

    def match(self, key: str, key_code: int) -> bool:
        """Return whether the given key_code matches the given key."""
        try:
            return self.keys[key].key_code == key_code
        except KeyError:
            return False

    def match_any(self, keys: typing.Sequence[str], key_code: int) -> bool:
        """Return whether the given key_code matches any of the given keys."""
        return any([self.match(key, key_code) for key in keys])

    def from_key_code(self, key_code: int) -> typing.Optional[str]:
        """Return an input string for a given key code."""
        for input_name, input_key in self.keys.items():
            if input_key.key_code == key_code:
                return input_name
        return None


GameMovement = KeyMap("game", "movement")
GameCommand = KeyMap("game", "command")
GameInterface = KeyMap("game", "interface")
