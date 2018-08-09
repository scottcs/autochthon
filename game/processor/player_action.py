"""Player action processor."""
from typing import Any

import esper

from game.component.hp import HP
from game.component.position import Position
from game.component.playercontrolled import PlayerControlled
from game.component.solid import Solid
from game.component.velocity import Velocity
from game.component.waiting import Waiting
from game.component.want_to_move import WantToMove
from game.types import Entity
from game.utils.time import GameTime


class PlayerActionProcessor(esper.Processor):
    """Player action processor.

    Determine what player action was meant.
    """
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process player components."""
        for ent, components in self.world.get_component(PlayerControlled):
            self.world.turn_time = self.process_player(ent)
            print(f'turn_time: {self.world.turn_time}')
            if self.world.turn_time == 0:
                print('stop processing')
                self.world.stop_processing = True
                return

    def process_player(self, ent: Entity) -> GameTime:
        """Process the player entity."""
        action_cost = self._check_waiting(ent)
        if not action_cost:
            action_cost = self._check_movement(ent)
        if not action_cost:
            action_cost = self._check_attack(ent)
        # TODO: resolve other kinds of collisions
        return action_cost

    def _check_waiting(self, ent: Entity) -> GameTime:
        for waiting in self.world.try_component(ent, Waiting):
            self.world.remove_component(ent, Waiting)
            return waiting.wait_time
        return GameTime(0)

    def _check_movement(self, ent: Entity) -> GameTime:
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
                    return velocity.cost
        return GameTime(0)

    def _check_attack(self, ent: Entity) -> GameTime:
        return GameTime(0)
