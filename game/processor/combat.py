"""Combat processor."""
from typing import Any

import esper

from game.component.attacking import Attacking
from game.component.actor import Actor
from game.component.dead import Dead
from game.component.hp import HP


class CombatProcessor(esper.Processor):
    """Combat processor."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process combat."""
        for ent, components in self.world.get_components(Attacking, Actor):
            attacking, actor = components
            existing = self.world.get_solid_entity_at_position(attacking.target_x,
                                                               attacking.target_y)
            if not existing:
                continue
            # TODO: find attack strength of attacker and defense strength of defender
            # TODO: move this to more systems (damage mitigation, damage taking, etc)
            for hp in self.world.try_component(existing, HP):
                hp.current -= 5
                if hp.current <= 0:
                    # TODO: clean up dead entities (convert to corpses? that decay?)
                    self.world.add_component(existing, Dead())
            self.world.remove_component(ent, Attacking)
            # TODO: move attack cost elsewhere and calculate from other components
            actor.time_units -= 100


