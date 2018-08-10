"""Component indicating an entity wants to move."""


class Moving:
    """Entity wants to move to destination position."""
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
