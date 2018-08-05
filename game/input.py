"""Input handling."""
import json
from pathlib import Path

from game.events import InputEvent, PlayerMovementEvent
from game.state import GameState
from game.types import EventType
from game.utils.geometry import Point

KEYS_JSON = Path('static') / Path('keys.json')


class InputHandler:
    """Handle input and issue events."""
    def __init__(self) -> None:
        InputEvent.handle(self.handle)
        with open(KEYS_JSON) as f:
            keys: dict = json.load(f)
        self.keys: dict = keys['Keys']
        self.keys_reverse: dict = {v: k for k, v in self.keys.items()}
        self.modifiers: dict = keys['Modifiers']
        self.modifiers_reverse: dict = {v: k for k, v in self.modifiers.items()}
        self.events: dict = keys['Events']
        self.events_reverse: dict = {v: k for k, v in self.events.items()}

    def handle(self, event: EventType) -> None:
        """Handle input event."""
        modifiers: dict = self._unpack_modifiers(event['modifiers'])
        key: str = self._get_key(event['code'])
        coords: Point = Point(event['x_coord'], event['y_coord'])
        if event.get('state', GameState.UNKNOWN) == GameState.PLAYING:
            print('playing')
            if event['event'] == self.events['KeyPress']:
                print('KeyPress')
                self.handle_keypress_playing(modifiers, key, coords)

    def _unpack_modifiers(self, modifiers: int) -> dict:
        return {
            'shift': modifiers & self.modifiers['Shift'] != 0,
            'ctrl': modifiers & self.modifiers['Ctrl'] != 0,
            'alt': modifiers & self.modifiers['Alt'] != 0,
        }

    def _get_key(self, code: int) -> str:
        try:
            return self.keys_reverse[code].lower()
        except KeyError:
            return chr(code).lower()

    @staticmethod
    def handle_keypress_playing(modifiers: dict, key: str, coords: Point) -> None:
        """Handle input event in the PLAYING state."""
        move_up = key in 'kyu'
        move_down = key in 'jbn'
        move_left = key in 'hyb'
        move_right = key in 'lun'
        dx = 0
        dy = 0
        if move_up:
            dy -= 1
        if move_down:
            dy += 1
        if move_left:
            dx -= 1
        if move_right:
            dx += 1
        PlayerMovementEvent({'dx': dx, 'dy': dy})
