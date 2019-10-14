"""Input handling class."""
import logging
import typing

import bearlibterminal.terminal as blt

import game.data
import game.events
import game.types

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

KEYCODES = {k[3:]: v for k, v in blt.__dict__.items() if k.startswith("TK_")}


def key_to_keycode(key: str) -> typing.Optional[int]:
    """Convert a key by name to a key code."""
    try:
        return KEYCODES[key.upper()]
    except IndexError:
        return None


class InputHandler:
    """Base Input Handler class."""

    def process(self) -> None:
        """Process input."""
        pass


class BearLibInput(InputHandler):
    """Input handler for bearlibterminal."""

    def process(self) -> None:
        """Check for input and fire an event if found."""
        super().process()
        if blt.has_input():
            input_key = game.types.InputKey(
                blt.read(),
                blt.check(blt.TK_SHIFT),
                blt.check(blt.TK_CONTROL),
                blt.check(blt.TK_ALT),
            )
            game.events.Input(event={"key": input_key})


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
            keycode = key_to_keycode(key_map["key"])
            if keycode is None:
                log.error(f"Could not determine keycode for {key_map}")
                continue
            keys[key.lower()] = game.types.InputKey(
                keycode, key_map["shift"], key_map["ctrl"], key_map["alt"]
            )
        self.keys = keys

    def match(self, key: str, input_key: game.types.InputKey) -> bool:
        """Return whether the given key_code matches the given input key."""
        try:
            return self.keys[key.lower()] == input_key
        except KeyError:
            return False

    def match_any(self, keys: typing.Sequence[str], input_key: game.types.InputKey) -> bool:
        """Return whether the given input key matches any of the given keys."""
        return any([self.match(key, input_key) for key in keys])

    def from_input_key(self, input_key: game.types.InputKey) -> typing.Optional[str]:
        """Return an input string for a given input key."""
        for input_name, my_input_key in self.keys.items():
            if my_input_key == input_key:
                return input_name
        return None


GameMovement = KeyMap("game", "movement")
GameCommand = KeyMap("game", "command")
GameInterface = KeyMap("game", "interface")
GameMenu = KeyMap("game", "command")
