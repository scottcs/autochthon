"""Attribute components."""
import dataclasses

import game.component.base
import game.types


class HP(game.component.base.BaseIntMinMaxComponent):
    """Hitpoint component."""


@dataclasses.dataclass
class TMPChangeHP:
    """Change the HP attribute."""

    amount: int
