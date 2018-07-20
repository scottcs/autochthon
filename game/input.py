"""Input handling."""

from game.events import InputEvent, PlayerMovementEvent
from game.state import GameState


class InputHandler:
    """Handle input and issue events."""
    def __init__(self):
        InputEvent.handle(self.handle)

    def handle(self, keys=None, mouse=None, state=None):
        """Handle input event."""
        if state == GameState.PLAYING:
            self.handle_playing(keys, mouse)

    @staticmethod
    def handle_playing(keys, mouse):
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
                PlayerMovementEvent(dx, dy)
