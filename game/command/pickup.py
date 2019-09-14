"""Pickup command."""
import game.command.base
import game.component.gamelog
import game.component.player


class Pickup(game.command.base.BaseCommand):
    """Pickup command."""

    def run(self) -> None:
        """Run the command."""
        for ent, _ in self.world.get_component(game.component.player.Player):
            item = self.world.pickup_item(ent)
            if not item:
                cmd_log = self.world.get_or_add_component(
                    ent, game.component.gamelog.GUTCommandLog
                )
                cmd_log.add(f"There is nothing to pick up!")
