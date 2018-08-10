"""Player bump processor."""
from typing import Any, Optional

import esper

from game.component.hp import HP
from game.component.position import Position
from game.component.player_bump import PlayerBump
from game.component.solid import Solid
from game.component.waiting import Waiting
from game.component.moving import Moving
from game.events import PlayerActedEvent
from game.types import Entity


class PlayerBumpProcessor(esper.Processor):
    """Player bump processor.

    Determine what player action was meant.
    """
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process player components."""
        for ent, bump in self.world.get_component(PlayerBump):
            self.process_player(ent, bump)
            self.world.remove_component(ent, PlayerBump)

    def process_player(self, ent: Entity, bump: PlayerBump) -> None:
        """Process the player entity."""
        if not self._check_waiting(ent, bump):
            position = self.world.component_for_entity(ent, Position)
            destination = Position(position.x + bump.dx, position.y + bump.dy)
            existing = self.world.get_solid_entity_at_position(destination.x, destination.y)
            if existing:
                self._try_attacking(ent, existing)
                # TODO: resolve other kinds of collisions? Digging?
            else:
                self._try_moving(ent, destination)

    def _check_waiting(self, ent: Entity, bump: PlayerBump) -> bool:
        if bump.dx == 0 and bump.dy == 0:
            self.world.add_component(ent, Waiting())
            PlayerActedEvent.fire()
            return True
        return False

    def _try_attacking(self, ent: Entity, other: Entity) -> None:
        for hp in self.world.try_component(other, HP):
            # TODO: add Attacking component
            PlayerActedEvent.fire()

    def _try_moving(self, ent: Entity, destination: Position):
        self.world.add_component(ent, Moving(destination.x, destination.y))
        PlayerActedEvent.fire()
