"""Player action processor."""
from typing import Any

import esper

from game.component.actor import Actor
from game.component.hp import HP
from game.component.position import Position
from game.component.playercontrolled import PlayerControlled
from game.component.solid import Solid
from game.component.velocity import Velocity
from game.component.waiting import Waiting
from game.component.want_to_move import WantToMove
from game.events import PlayerActedEvent
from game.types import Entity


class PlayerActionProcessor(esper.Processor):
    """Player action processor.

    Determine what player action was meant.
    """
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process player components."""
        for ent, components in self.world.get_component(PlayerControlled):
            self.process_player(ent)

    def process_player(self, ent: Entity):
        """Process the player entity."""
        self._check_waiting(ent)
        self._check_movement(ent)
        self._check_attack(ent)
        # TODO: resolve other kinds of collisions

    def _check_waiting(self, ent: Entity):
        for waiting in self.world.try_component(ent, Waiting):
            for actor in self.world.try_component(ent, Actor):
                # TODO: This should maybe be in the movement system
                actor.time_units -= waiting.wait_time
            self.world.remove_component(ent, Waiting)
            PlayerActedEvent.fire()

    def _check_movement(self, ent: Entity):
        if self.world.has_component(ent, WantToMove):
            position = self.world.component_for_entity(ent, Position)
            velocity = self.world.component_for_entity(ent, Velocity)
            new_position = (position.x + velocity.x, position.y + velocity.y)
            if self.world.has_component(ent, Solid):
                found = self.world.occupied.get(new_position, None)
                if found:
                    self.world.remove_component(ent, WantToMove)
                    self.world.remove_component(ent, Velocity)
                    if self.world.has_component(found, HP):
                        # TODO: add WantToAttack
                        pass
                else:
                    self.world.occupied[(position.x, position.y)] = None
                    self.world.occupied[new_position] = ent
                    PlayerActedEvent.fire()

    def _check_attack(self, ent: Entity):
        pass
