"""Pickup command."""
from game.component.player import Player
from game.component.gamelog import GUTCommandLog
from .base import BaseCommand


class PickupCommand(BaseCommand):
    """Pickup command."""

    def run(self) -> None:
        """Run the command."""
        for ent, _ in self.world.get_component(Player):
            item = self.world.pickup_item(ent)
            if not item:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add(f"There is nothing to pick up!")
