"""Player bump processor."""
from typing import Any

import esper

from game.component.ai import Enemy
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
            enemy = self.world.get_enemy_at_position(destination.x, destination.y)
            if enemy:
                self._try_attacking(ent, enemy)
            elif self.world.map.walkable[destination.y, destination.x]:
                self._try_moving(ent, destination)
            # TODO: resolve other kinds of collisions? Digging?

    def _check_waiting(self, ent: Entity, bump: GUTPlayerBump) -> bool:
        if bump.dx == 0 and bump.dy == 0:
            self.world.add_component(ent, GUTWaiting())
            PlayerActedEvent.fire()
            return True
        return False

    def _try_attacking(self, ent: Entity, other: Entity) -> None:
        other_hp = self.world.optional_component_for_entity(other, HP)
        other_pos = self.world.optional_component_for_entity(other, Position)
        if other_hp and other_pos:
            target = GUTCurrentTarget(other_pos.x, other_pos.y, AttackType.melee, other)
            self.world.add_component(ent, target)
            PlayerActedEvent.fire()

    def _try_moving(self, ent: Entity, destination: Position) -> None:
        self.world.add_component(ent, GUTMoving(destination.x, destination.y))
        PlayerActedEvent.fire()
