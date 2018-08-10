"""Attacking component."""


class Attacking:
    """Entity is attacking."""
    def __init__(self, target_x: int, target_y: int) -> None:
        self.target_x: int = target_x
        self.target_y: int = target_y
