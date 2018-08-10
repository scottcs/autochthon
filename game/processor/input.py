"""User input processing."""
import json
from pathlib import Path
from typing import Any

import esper

from game.component.position import Position
from game.component.playercontrolled import PlayerControlled
from game.component.velocity import Velocity
from game.component.waiting import Waiting
from game.component.want_to_move import WantToMove
from game.events import InputEvent
from game.types import EventType, GameState
from game.utils.geometry import Point

KEYS_JSON = Path('static') / Path('keys.json')


class InputProcessor(esper.Processor):
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
        move_up = key in 'kyu'
        move_down = key in 'jbn'
        move_left = key in 'hyb'
        move_right = key in 'lun'
        wait = key == 'period'

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

        if not (dx or dy or wait):
            return

        if dx or dy:
            for ent, components in self.world.get_components(PlayerControlled, Position):
                self.world.add_component(ent, WantToMove())
                self.world.add_component(ent, Velocity(dx, dy, 100))

        if wait:
            for ent, _ in self.world.get_component(PlayerControlled):
                self.world.add_component(ent, Waiting())
