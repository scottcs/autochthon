"""User input processing."""
import json
from pathlib import Path
from typing import Any

import esper

from game.component.player_bump import PlayerBump
from game.component.player_controlled import PlayerControlled
from game.events import InputEvent
from game.types import EventType, GameState
from game.utils.geometry import Point

KEYS_JSON = Path('static') / Path('keys.json')


class PlayerInputProcessor(esper.Processor):
    """Process user input and issue events."""
    def __init__(self) -> None:
        super().__init__()
        self.input_queue: list = []
        InputEvent.handle(self._on_input)
        with open(KEYS_JSON) as f:
            keys: dict = json.load(f)
        self.keys: dict = keys['Keys']
        self.keys_reverse: dict = {v: k for k, v in self.keys.items()}
        self.modifiers: dict = keys['Modifiers']
        self.events: dict = keys['Events']

    def _on_input(self, event: EventType) -> None:
        modifiers: dict = self._unpack_modifiers(event['modifiers'])
        key: str = self._get_key(event['code'])
        coords: Point = Point(event['x_coord'], event['y_coord'])
        self.input_queue.append({
            'event': event['event'],
            'state': event.get('state', GameState.UNKNOWN),
            'modifiers': modifiers,
            'key': key,
            'coords': coords,
        })

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process the input queue."""
        while self.input_queue:
            event = self.input_queue.pop()
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

    def handle_keypress_playing(self, _modifiers: dict, key: str, _coords: Point):
        """Handle input event in the PLAYING state."""
        bump_up = key in 'kyu'
        bump_down = key in 'jbn'
        bump_left = key in 'hyb'
        bump_right = key in 'lun'
        wait = key == 'period'

        dx = 0
        dy = 0
        if bump_up:
            dy -= 1
        if bump_down:
            dy += 1
        if bump_left:
            dx -= 1
        if bump_right:
            dx += 1

        if not (dx or dy or wait):
            return

        for ent, _ in self.world.get_component(PlayerControlled):
            self.world.add_component(ent, PlayerBump(dx, dy))
