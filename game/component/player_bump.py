"""Player bump component."""


class PlayerBump:
    """Player wants to do something that passes time, maybe in a direction."""
    def __init__(self, dx: int=0, dy: int=0) -> None:
        self.dx: int = dx
        self.dy: int = dy
