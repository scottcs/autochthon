"""ECS world, based on esper's World, but keeps track of the Player and prioritizes it."""
import logging
from typing import Any, Optional, Set, Callable, Tuple, Generator

import esper

from game.component.action import Actor, GUTMyTurn
from game.component.ai import Enemy
from game.component.container import Item, GUTContainerTransfer
from game.component.status import GUTDead
from game.component.player import Player
from game.component.movement import Position
from game.core.map import Map
from game.types import ProcessGroup, Entity, ComponentSchema

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class World(esper.World):
    """Esper's World class that always iterates the Player first."""

    def __init__(self, timed: bool = False) -> None:
        super().__init__(timed)
        self._processor_groups: dict = {}
        self.map: Optional[Map] = None
        self.players: Set[Entity] = set()

    def add_processor(
        self,
        processor_instance: esper.Processor,
        priority: int = 0,
        group: Optional[ProcessGroup] = None,
    ) -> None:
        """Add a Processor instance to the World.

        :param processor_instance: An instance of a Processor,
        subclassed from the Processor class
        :param priority: A higher number is processed first.
        :param group: Process group to add processor to.
        """
        super().add_processor(processor_instance, priority=priority)
        group = group or ProcessGroup.default
        self._processor_groups.setdefault(group, [])
        self._processor_groups[group].append(processor_instance)
        self._processor_groups[group].sort(key=lambda p: p.priority, reverse=True)

    def remove_processor(self, processor_type: esper.Processor) -> None:
        """Remove a processor."""
        for group in self._processor_groups.values():
            for processor in group:
                if type(processor) == processor_type:
                    group.remove(processor)
        super().remove_processor(processor_type)

    def process_group(self, group: ProcessGroup, *args: Any, **kwargs: Any) -> None:
        """Process a group of processors."""
        self._clear_dead_entities()
        for processor in self._processor_groups[group]:
            processor.process(*args, **kwargs)

    def any_actors_can_act(self) -> bool:
        """Return true if any actors can act."""
        for ent, actor in self.get_component(Actor):
            if not self.has_component(ent, GUTDead):
                if actor.time_units >= 0:
                    return True
        return False

    def actor_take_action(
            self, ent: Entity, actor: Actor, cost: int, *remove_components: Any
    ) -> None:
        """Have an actor take an action."""
        actor.time_units -= cost
        try:
            self.remove_component(ent, GUTMyTurn)
        except KeyError:
            pass
        for component in remove_components:
            try:
                self.remove_component(ent, component)
            except KeyError:
                pass

    def kill_entity(self, ent: Entity):
        """Kill an entity."""
        try:
            self.remove_component(ent, GUTMyTurn)
        except KeyError:
            pass
        self.add_component(ent, GUTDead())

    def pickup_item(self, ent: Entity) -> Optional[Entity]:
        """Pick up an item at an entity's location and return its id."""
        at = self.component_for_entity(ent, Position)
        item_ent = self.get_item_at_position(at.x, at.y)
        if item_ent:
            self.add_component(item_ent, GUTContainerTransfer(ent))
            return item_ent
        return None

    def drop_item(self, ent: Entity, item: Entity) -> bool:
        """Drop an item onto the map where the entity is."""
        at = self.component_for_entity(ent, Position)
        item_ent = self.get_item_at_position(at.x, at.y)
        if item_ent:
            return False
        self.add_component(item, GUTContainerTransfer())
        return True

    def get_enemy_at_position(self, x: int, y: int) -> Optional[Entity]:
        """Get an enemy entity at the given position."""
        if self.map[x, y].contains_enemy:
            enemy = self.get_entity_at_position(x, y, Enemy)
            if enemy:
                return enemy
            else:
                log.error("Map and components out of sync for enemy location!")
        return None

    def get_item_at_position(self, x: int, y: int) -> Optional[Entity]:
        """Get an item entity at the given position."""
        if self.map[x, y].contains_item:
            item = self.get_entity_at_position(x, y, Item)
            if item:
                return item
            else:
                log.error("Map and components out of sync for item location!")
        return None

    def get_entity_at_position(
        self, x: int, y: int, *required_components: Any
    ) -> Optional[Entity]:
        """Get a single entity at the given position (the first found)."""
        for ent, components in self.get_components(Position, *required_components):
            other_pos = components[0]
            if other_pos.x == x and other_pos.y == y:
                return ent
        return None

    def entities_at_position(
        self, x: int, y: int, *required_components: Any
    ) -> Generator[Entity, None, None]:
        """Yield any entities at the given position, with the optional required components."""
        for ent, components in self.get_components(Position, *required_components):
            other_pos = components[0]
            if other_pos.x == x and other_pos.y == y:
                yield ent

    def _get_component(self, component_type: Any) -> Any:
        """Get an iterator for Entity, Component pairs.

        :param component_type: The Component type to retrieve.
        :return: An iterator for (Entity, Component) tuples.
        """
        entity_db = self._entities
        players = set()

        for entity in self._components.get(Player, []):
            players.add(entity)
            try:
                yield entity, entity_db[entity][component_type]
            except KeyError:
                pass
        for entity in self._components.get(component_type, []):
            if entity not in players:
                yield entity, entity_db[entity][component_type]

    def _get_components(self, *component_types: Any) -> Any:
        """Get an iterator for Entity and multiple Component sets.

        :param component_types: Two or more Component types.
        :return: An iterator for Entity, (Component1, Component2, etc)
        tuples.
        """

        entity_db = self._entities
        comp_db = self._components
        players = set()

        for entity in self._components.get(Player, []):
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

    def try_component(self, entity: Entity, component_type: Any) -> Any:
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

    def optional_component_for_entity(self, entity: Entity, component_type: Any) -> Optional[Any]:
        """Retrieve a Component instance for a specific Entity.

        Retrieve a Component instance for a specific Entity. In some cases,
        it may be necessary to access a specific Component instance.
        For example: directly modifying a Component to handle user input.

        Returns None if the given Entity and Component do not exist.
        :param entity: The Entity ID to retrieve the Component for.
        :param component_type: The Component instance you wish to retrieve.
        :return: The Component instance requested for the given Entity ID.
        """
        try:
            return self.component_for_entity(entity, component_type)
        except KeyError:
            return None

    def get_or_add_component(
        self, entity: Entity, component_type: Any, *args: Any, **kwargs: Any
    ) -> Any:
        """Get a component for the given entity if it exists, or else create a new one."""
        try:
            return self.component_for_entity(entity, component_type)
        except KeyError:
            comp = component_type(*args, **kwargs)
            self.add_component(entity, comp)
            return comp

    def assemble_entity(self, schema: Tuple[ComponentSchema], *variations: Callable) -> Entity:
        """Assemble an entity from a schema and a list of optional variation functions."""
        components = []
        for component_type, args, kwargs in schema:
            components.append(component_type(*args, **kwargs))
        entity: Entity = self.create_entity(*components)
        for variation in variations:
            variation(self, entity)
        return entity
