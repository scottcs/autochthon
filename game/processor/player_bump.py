"""Player bump processor."""
import typing

import esper

import game.component.attack
import game.component.attribute
import game.component.movement
import game.component.player
import game.types


class PlayerBumpProcessor(esper.Processor):
    """Player bump processor.

    Determine what player action was meant.
    """

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process player components."""
        for ent, bump in self.world.get_component(game.component.player.GUTPlayerBump):
            self.process_player(ent, bump)
            self.world.remove_component(ent, game.component.player.GUTPlayerBump)

    def process_player(
        self, ent: game.types.Entity, bump: game.component.player.GUTPlayerBump
    ) -> None:
        """Process the player entity."""
        if not self._check_waiting(ent, bump):
            position = self.world.component_for_entity(ent, game.component.movement.Position)
            destination = game.component.movement.Position(
                position.x + bump.dx, position.y + bump.dy
            )
            enemy = self.world.get_enemy_at_position(destination.x, destination.y)
            if enemy:
                self._try_attacking(ent, enemy)
            elif self.world.map.walkable[destination.y, destination.x]:
                self._try_moving(ent, destination)
            # TODO: resolve other kinds of collisions? Digging?

    def _check_waiting(
        self, ent: game.types.Entity, bump: game.component.player.GUTPlayerBump
    ) -> bool:
        if bump.dx == 0 and bump.dy == 0:
            self.world.add_component(ent, game.component.movement.GUTWaiting())
            return True
        return False

    def _try_attacking(self, ent: game.types.Entity, other: game.types.Entity) -> None:
        other_hp = self.world.optional_component_for_entity(other, game.component.attribute.HP)
        other_pos = self.world.optional_component_for_entity(
            other, game.component.movement.Position
        )
        if other_hp and other_pos:
            target = game.component.attack.GUTCurrentTarget(
                other_pos.x, other_pos.y, game.types.Attack.melee, other
            )
            self.world.add_component(ent, target)

    def _try_moving(
        self, ent: game.types.Entity, destination: game.component.movement.Position
    ) -> None:
        self.world.add_component(
            ent, game.component.movement.GUTMoving(destination.x, destination.y)
        )
