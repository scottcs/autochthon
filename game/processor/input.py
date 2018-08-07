"""User input processing."""
import json
from pathlib import Path

import esper

from game.component.position import Position
from game.component.playercontrolled import PlayerControlled
from game.component.velocity import Velocity
from game.events import InputEvent, MoveEntityEvent, GameTimeEvent
from game.state import GameState
from game.types import EventType
from game.utils.geometry import Point

KEYS_JSON = Path('static') / Path('keys.json')


class InputProcessor(esper.Processor):
    """Process user input and issue events."""
    def __init__(self) -> None:
        super().__init__()
        self._input_queue = []
        InputEvent.handle(self.on_input)
        with open(KEYS_JSON) as f:
            keys: dict = json.load(f)
        self.keys: dict = keys['Keys']
        self.keys_reverse: dict = {v: k for k, v in self.keys.items()}
        self.modifiers: dict = keys['Modifiers']
        self.events: dict = keys['Events']

    def on_input(self, event: EventType) -> None:
        """Handle input event."""
        modifiers: dict = self._unpack_modifiers(event['modifiers'])
        key: str = self._get_key(event['code'])
        coords: Point = Point(event['x_coord'], event['y_coord'])
        self._input_queue.append({
            'event': event['event'],
            'state': event.get('state', GameState.UNKNOWN),
            'modifiers': modifiers,
            'key': key,
            'coords': coords,
        })

    def process(self, *args, **kwargs):
        """Process the input queue."""
        while self._input_queue:
            event = self._input_queue.pop()
            if event['event'] == self.events['KeyPress']:
                if event['state'] == GameState.PLAYING:
                    self.handle_keypress_playing(event['modifiers'], event['key'], event['coords'])

    def _unpack_modifiers(self, modifiers: int) -> dict:
        return {
            'shift': modifiers & self.modifiers['Shift'] != 0,
            'ctrl': modifiers & self.modifiers['Ctrl'] != 0,
            'alt': modifiers & self.modifiers['Alt'] != 0,
        }

    def _get_key(self, code: int) -> str:
        try:
            return str(self.keys_reverse[code]).lower()
        except KeyError:
            return chr(code).lower()

    def handle_keypress_playing(self, _modifiers: dict, key: str, _coords: Point) -> None:
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
        for entity, components in self.world.get_components(PlayerControlled, Position, Velocity):
            MoveEntityEvent({'entity': entity, 'velocity': components[-1], 'dx': dx, 'dy': dy})
        GameTimeEvent.fire()
