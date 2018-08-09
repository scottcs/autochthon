"""Toggleable component."""


class Toggleable:
    """Toggleable component, like a door or switch."""
    def __init__(self, initial_state: bool=False) -> None:
        self.state: bool = initial_state

    def toggle(self) -> None:
        """Toggle state."""
        self.state = not self.state
