"""Player bump processor."""
from typing import Any

import esper

from game.component.attack import GUTCurrentTarget
from game.component.attribute import HP
from game.component.player import GUTPlayerBump
from game.component.movement import GUTMoving, GUTWaiting, Position
from game.events import PlayerActedEvent
from game.types import AttackType, Entity


class PlayerBumpProcessor(esper.Processor):
    """Player bump processor.

    Determine what player action was meant.
    """
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process player components."""
        for ent, bump in self.world.get_component(GUTPlayerBump):
            self.process_player(ent, bump)
            self.world.remove_component(ent, GUTPlayerBump)

    def process_player(self, ent: Entity, bump: GUTPlayerBump) -> None:
        """Process the player entity."""
        if not self._check_waiting(ent, bump):
            position = self.world.component_for_entity(ent, Position)
            destination = Position(position.x + bump.dx, position.y + bump.dy)
            existing = self.world.get_solid_entity_at_position(destination.x, destination.y)
            if existing:
                self._try_attacking(ent, existing)
            elif self.world.map[destination.x, destination.y].walkable:
                self._try_moving(ent, destination)
            # TODO: resolve other kinds of collisions? Digging?

    def _check_waiting(self, ent: Entity, bump: GUTPlayerBump) -> bool:
        if bump.dx == 0 and bump.dy == 0:
            self.world.add_component(ent, GUTWaiting())
            PlayerActedEvent.fire()
            return True
        return False

    def _try_attacking(self, ent: Entity, other: Entity) -> None:
        for _ in self.world.try_component(other, HP):
            for other_pos in self.world.try_component(other, Position):
                target = GUTCurrentTarget(other_pos.x, other_pos.y, AttackType.melee, other)
                self.world.add_component(ent, target)
                PlayerActedEvent.fire()

    def _try_moving(self, ent: Entity, destination: Position) -> None:
        self.world.add_component(ent, GUTMoving(destination.x, destination.y))
        PlayerActedEvent.fire()
