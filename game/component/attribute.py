"""Attribute components."""
from dataclasses import dataclass
from game.component.base import BaseIntMinMaxComponent
from game.types import Number


class HP(BaseIntMinMaxComponent):
    """Hitpoint component."""


@dataclass
class GUTChangeHP:
    """Change the HP attribute."""

    amount: Number
