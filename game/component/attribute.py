"""Attribute components."""
from game.component.base import BaseIntMinMaxComponent
from game.types import Number


class HP(BaseIntMinMaxComponent):
    """Hitpoint component."""


class GUTChangeHP:
    """Change the HP attribute."""
    def __init__(self, amount: Number) -> None:
        self.amount: Number = amount
