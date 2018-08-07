"""Positional component."""


class Positional:
    """Positional component."""
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
        self.prev_x: int = x
        self.prev_y: int = y

    def save_previous(self) -> None:
        """Save the current position as the previous position."""
        self.prev_x = self.x
        self.prev_y = self.y

    def reset_to_previous(self) -> None:
        """Reset the position to the previous position."""
        self.x = self.prev_x
        self.y = self.prev_y
