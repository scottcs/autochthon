"""ECS world, based on esper's World, but keeps track of the Player and prioritizes it."""
import logging
import typing

import esper

import game.component.action
import game.component.ai
import game.component.container
import game.component.movement
import game.component.player
import game.component.status
import game.core.map
import game.events
import game.types

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class World(esper.World):
    """Esper's World class that always iterates the Player first."""

    def __init__(self, timed: bool = False) -> None:
        super().__init__(timed)
        self._processor_groups: dict = {}
        self.map: typing.Optional[game.core.map.Map] = None
        self.players: typing.Set[game.types.Entity] = set()

    def add_processor(
        self,
        processor_instance: esper.Processor,
        priority: int = 0,
        group: typing.Optional[game.types.ProcessGroup] = None,
    ) -> None:
        """Add a Processor instance to the World.

        :param processor_instance: An instance of a Processor,
        subclassed from the Processor class
        :param priority: A higher number is processed first.
        :param group: Process group to add processor to.
        """
        super().add_processor(processor_instance, priority=priority)
        group = group or game.types.ProcessGroup.default
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

    def process_group(
        self, group: game.types.ProcessGroup, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Process a group of processors."""
        self._clear_dead_entities()
        for processor in self._processor_groups[group]:
            processor.process(*args, **kwargs)

    def actor_takes_turn(self, ent: game.types.Entity, *remove_components: typing.Any) -> None:
        """Clean up after an actor takes a turn."""
        try:
            self.remove_component(ent, game.component.action.TMPMyTurn)
        except KeyError:
            pass
        for component in remove_components:
            try:
                self.remove_component(ent, component)
            except KeyError:
                pass

    def kill_entity(self, ent: game.types.Entity) -> None:
        """Kill an entity."""
        try:
            self.remove_component(ent, game.component.action.TMPMyTurn)
        except KeyError:
            pass
        self.add_component(ent, game.component.status.TMPDead())
        game.events.RenderEntities.fire()

    def pickup_item(self, ent: game.types.Entity) -> typing.Optional[game.types.Entity]:
        """Pick up an item at an entity's location and return its id."""
        at = self.component_for_entity(ent, game.component.movement.Position)
        item_ent = self.get_item_at_position(at.x, at.y)
        if item_ent:
            self.add_component(item_ent, game.component.container.TMPTransfer(ent))
            game.events.RenderEntities.fire()
            return item_ent
        return None

    def drop_item(self, ent: game.types.Entity, item_ent: game.types.Entity) -> bool:
        """Drop an item onto the map where the entity is."""
        at = self.component_for_entity(ent, game.component.movement.Position)
        current_item_ent = self.get_item_at_position(at.x, at.y)
        if current_item_ent:
            return False
        self.add_component(item_ent, game.component.container.TMPTransfer())
        game.events.RenderEntities.fire()
        return True

    def get_enemy_at_position(self, x: int, y: int) -> typing.Optional[game.types.Entity]:
        """Get an enemy entity at the given position."""
        if self.map and self.map.contains_enemy[y, x]:
            enemy = self.get_entity_at_position(x, y, game.component.ai.Enemy)
            if enemy:
                return enemy
            else:
                log.error("Map and components out of sync for enemy location!")
        return None

    def get_item_at_position(self, x: int, y: int) -> typing.Optional[game.types.Entity]:
        """Get an item entity at the given position."""
        if self.map and self.map.contains_item[y, x]:
            item = self.get_entity_at_position(x, y, game.component.container.Item)
            if item:
                return item
            else:
                log.error("Map and components out of sync for item location!")
        return None

    def get_entity_at_position(
        self, x: int, y: int, *required_components: typing.Any
    ) -> typing.Optional[game.types.Entity]:
        """Get a single entity at the given position (the first found)."""
        for ent, components in self.get_components(
            game.component.movement.Position, *required_components
        ):
            other_pos = components[0]
            if other_pos.x == x and other_pos.y == y:
                return ent
        return None

    def entities_at_position(
        self, x: int, y: int, *required_components: typing.Any
    ) -> typing.Generator[game.types.Entity, None, None]:
        """Yield any entities at the given position, with the optional required components."""
        for ent, components in self.get_components(
            game.component.movement.Position, *required_components
        ):
            other_pos = components[0]
            if other_pos.x == x and other_pos.y == y:
                yield ent

    # def _get_component(self, component_type: typing.Any) -> typing.Any:
    #     """Get an iterator for Entity, Component pairs.
    #
    #     :param component_type: The Component type to retrieve.
    #     :return: An iterator for (Entity, Component) tuples.
    #     """
    #     entity_db = self._entities
    #     players = set()
    #
    #     for entity in self._components.get(game.component.player.Player, []):
    #         players.add(entity)
    #         try:
    #             yield entity, entity_db[entity][component_type]
    #         except KeyError:
    #             pass
    #     for entity in self._components.get(component_type, []):
    #         if entity not in players:
    #             yield entity, entity_db[entity][component_type]
    #
    # def _get_components(self, *component_types: typing.Any) -> typing.Any:
    #     """Get an iterator for Entity and multiple Component sets.
    #
    #     :param component_types: Two or more Component types.
    #     :return: An iterator for Entity, (Component1, Component2, etc)
    #     tuples.
    #     """
    #
    #     entity_db = self._entities
    #     comp_db = self._components
    #     players = set()
    #
    #     for entity in self._components.get(game.component.player.Player, []):
    #         players.add(entity)
    #         try:
    #             yield entity, [entity_db[entity][ct] for ct in component_types]
    #         except KeyError:
    #             pass
    #     try:
    #         for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
    #             if entity not in players:
    #                 yield entity, [entity_db[entity][ct] for ct in component_types]
    #     except KeyError:
    #         pass

    def try_component(self, entity: game.types.Entity, component_type: typing.Any) -> typing.Any:
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

    def optional_component_for_entity(
        self, entity: game.types.Entity, component_type: typing.Any
    ) -> typing.Optional[typing.Any]:
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
        self,
        entity: game.types.Entity,
        component_type: typing.Any,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Get a component for the given entity if it exists, or else create a new one."""
        try:
            return self.component_for_entity(entity, component_type)
        except KeyError:
            comp = component_type(*args, **kwargs)
            self.add_component(entity, comp)
            return comp
