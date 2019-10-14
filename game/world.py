"""ECS world, based on esper's World, with more utilities."""
import logging
import typing

import esper

import game.component.action
import game.component.ai
import game.component.container
import game.component.movement
import game.component.player
import game.component.status
import game.events
import game.map
import game.types

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class World(esper.World):
    """Esper's World class that always iterates the Player first."""

    def __init__(self, timed: bool = False) -> None:
        super().__init__(timed)
        self.map: typing.Optional[game.map.Map] = None
        self.players: typing.Set[game.types.Entity] = set()

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
        game.events.RenderEntities()

    def pickup_item(self, ent: game.types.Entity) -> typing.Optional[game.types.Entity]:
        """Pick up an item at an entity's location and return its id."""
        at = self.component_for_entity(ent, game.component.movement.Position)
        item_ent = self.get_item_at_position(at.x, at.y)
        if item_ent:
            self.add_component(item_ent, game.component.container.TMPTransfer(ent))
            game.events.RenderEntities()
            return item_ent
        return None

    def drop_item(self, ent: game.types.Entity, item_ent: game.types.Entity) -> bool:
        """Drop an item onto the map where the entity is."""
        at = self.component_for_entity(ent, game.component.movement.Position)
        current_item_ent = self.get_item_at_position(at.x, at.y)
        if current_item_ent:
            return False
        self.add_component(item_ent, game.component.container.TMPTransfer())
        game.events.RenderEntities()
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

    def entity_exists(self, ent: int) -> bool:
        """Determine whether an entity exists in the world."""
        return ent in self._entities

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
