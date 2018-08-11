"""Attribute components."""
from game.component.base_components import BaseIntMinMaxComponent
from game.types import Number


class HP(BaseIntMinMaxComponent):
    """Hitpoint component."""


class ChangeHP:
    """Change the HP attribute."""
    def __init__(self, amount: Number) -> None:
        self.amount: Number = amount
