"""ECS world, based on esper's World, but keeps track of the Player and prioritizes it."""
import esper

from game.component.playercontrolled import PlayerControlled


class World(esper.World):
    """Esper's World class that always iterates the Player first."""
    def _get_component(self, component_type):
        """Get an iterator for Entity, Component pairs.

        :param component_type: The Component type to retrieve.
        :return: An iterator for (Entity, Component) tuples.
        """
        entity_db = self._entities
        players = set()

        for entity in self._components.get(PlayerControlled, []):
            players.add(entity)
            try:
                yield entity, entity_db[entity][component_type]
            except KeyError:
                pass
        for entity in self._components.get(component_type, []):
            if entity not in players:
                yield entity, entity_db[entity][component_type]

    def _get_components(self, *component_types):
        """Get an iterator for Entity and multiple Component sets.

        :param component_types: Two or more Component types.
        :return: An iterator for Entity, (Component1, Component2, etc)
        tuples.
        """

        entity_db = self._entities
        comp_db = self._components
        players = set()

        for entity in self._components.get(PlayerControlled, []):
            players.add(entity)
            try:
                yield entity, [entity_db[entity][ct] for ct in component_types]
            except KeyError:
                pass
        try:
            for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
                if entity not in players:
                    yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass



