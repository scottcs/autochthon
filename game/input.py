"""Input handling."""
from typing import Optional

from game.events import InputEvent, PlayerMovementEvent
from game.state import GameState
from game.types import EventType


class InputHandler:
    """Handle input and issue events."""
    def __init__(self) -> None:
        InputEvent.handle(self.handle)

    def handle(self, event: EventType) -> None:
        """Handle input event."""
        if event.get('state', GameState.UNKNOWN) == GameState.PLAYING:
            self.handle_playing(event.get('keys'), event.get('mouse'))

    @staticmethod
    def handle_playing(keys: Optional[list]=None, mouse: Optional[list]=None) -> None:
        """Handle input event in the PLAYING state."""
        if keys:
            for key in keys:
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
