"""ECS world, based on esper's World, but keeps track of the Player and prioritizes it."""
from enum import Enum, auto

import esper

from game.component.playercontrolled import PlayerControlled
from game.component.position import Position
from game.component.solid import Solid


class ProcessGroup(Enum):
    """Groups of processors."""
    pre_turn = auto()
    turn = auto()
    post_turn = auto()


class World(esper.World):
    """Esper's World class that always iterates the Player first."""
    def __init__(self, timed=False):
        super().__init__(timed)
        self._processor_groups = {}
        self.occupied = {}
        self.stop_processing = False

    def add_processor(self, processor_instance, priority=0, group=None):
        """Add a Processor instance to the World.

        :param processor_instance: An instance of a Processor,
        subclassed from the Processor class
        :param priority: A higher number is processed first.
        :param group: Process group to add processor to.
        """
        super().add_processor(processor_instance, priority=priority)
        group = group or ProcessGroup.turn
        self._processor_groups.setdefault(group, [])
        self._processor_groups[group].append(processor_instance)

    def remove_processor(self, processor_type):
        """Remove a processor."""
        for group in self._processor_groups.values():
            for processor in group:
                if type(processor) == processor_type:
                    group.remove(processor)
        super().remove_processor(processor_type)

    def process_group(self, group, *args, **kwargs):
        """Process a group of processors."""
        self._clear_dead_entities()
        self.calculate_occupied()
        for processor in self._processor_groups[group]:
            if self.stop_processing:
                self.stop_processing = False
                return
            processor.process(*args, **kwargs)

    def calculate_occupied(self):
        """Calculate occupied map positions."""
        self.occupied.clear()
        for ent, components in self.get_components(Position, Solid):
            position = components[0]
            self.occupied[(position.x, position.y)] = ent

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

    def try_component(self, entity, component_type):
        """Try to get a single component type for an Entity.

          This method will return the requested Component if it exists, but
          will pass silently if it does not. This allows a way to access optional
          Components that may or may not exist.

          :param entity: The Entity ID to retrieve the Component for.
          :param component_type: The Component instance you wish to retrieve.
          :return: The single Component instance requested, or None
          """
        if component_type in self._entities[entity]:
            yield self._entities[entity][component_type]

