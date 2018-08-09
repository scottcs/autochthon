"""Hitpoint component."""
from typing import Optional


class HP:
    """Hitpoint component."""
    def __init__(self, initial: int=1, maximum: Optional[int]=None) -> None:
        self.current: int = initial
        self.max: int = maximum or initial

    def set_to_max(self):
        """Set current HP to maximum."""
        self.current = self.max
