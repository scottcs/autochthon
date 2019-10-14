"""Show game log command."""
import logging

import game.command.base
import game.processor.gamelog

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ShowLog(game.command.base.BaseCommand):
    """ShowLog command."""

    def run(self) -> None:
        """Run the command."""

        for log_component in game.processor.gamelog.buffer:
            log.debug(str(log_component))
