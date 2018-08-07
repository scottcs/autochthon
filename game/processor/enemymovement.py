"""Enemy movement processor."""
from random import randint
from typing import Any

import esper

from game.component.positional import Positional
from game.types import Entity


class EnemyMovementProcessor(esper.Processor):
    """Enemy movement processor."""

    def __init__(self) -> None:
        super().__init__()

    def process(self, *args: Any) -> None:
        """Process player movement events."""
        for enemy, enemy_pos in self.world.get_component(Positional):
            if enemy != self.world.player:
                enemy_pos.x = randint(0, 99)
                enemy_pos.y = randint(0, 99)
