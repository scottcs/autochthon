"""Factory utilities."""
import logging
from typing import Any, Optional, MutableSequence, Mapping, MutableMapping

from game.component.movement import Position
from game.utils.dataloader import DataLoader
from game.types import Entity
from game.utils.geometry import Point
from game.utils.random import parse, RNGCache, GameRNG
from game.utils.render import TileCache
from game.core.world import World

ON_CREATE = '=='

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class FactoryException(Exception):
    """Factory exceptions."""


def convert_datum(value: Any) -> Any:
    """Convert a data value to a global class.attribute value, if possible."""
    try:
        class_type, attr = value.split('.')
    except (ValueError, AttributeError):
        # the value does not have two parts separated by '.', or is not a string
        return None

    if class_type == 'Palette':
        from gamedata.palette import Palette
        result = getattr(Palette, attr)
    elif class_type == 'RenderLayer':
        from game.types import RenderLayer
        result = getattr(RenderLayer, attr)
    else:
        # allow exception to be raised here if it doesn't exist
        result = getattr(globals()[class_type], attr)
    return result


def get_component_class(class_substring: str) -> Any:
    """Get a component class from a substring like `attack.AttackCostModifier`."""
    component_group, component_class = class_substring.split('.')
    mod_name = f'game.component.{component_group}'
    _tmp = __import__(mod_name, globals=globals(), locals=locals(), fromlist=[component_class])
    return getattr(_tmp, component_class)


def validate_kwargs(kwargs: MutableMapping) -> None:
    """Validate keyword arguments for components."""
    for key, value in kwargs.items():
        if value is None:
            raise TypeError(f'Value for "{key}" must be specified.')
        if key == 'tile_id':
            try:
                value = int(value)
            except ValueError:
                id_ = TileCache.id_from_name(value)
                if id_ is None:
                    raise ValueError(f'Cannot find tile id for {value}')
                value = int(id_)
            kwargs[key] = value


class BaseEntityFactory:
    """Entity Factory."""

    def __init__(self, loader: DataLoader, world: World) -> None:
        self._loader: DataLoader = loader
        self._world: World = world
        self._rng: Optional[GameRNG] = None
        self._data_key: Optional[str] = None

    def make(self, templates: MutableSequence[str]) -> Entity:
        """Make an entity."""
        raise NotImplementedError('Must implement in child class.')

    def place_entity(self, ent: Entity, at: Point) -> None:
        """Place an entity at the given position in the world."""
        pos = self._world.component_for_entity(ent, Position)
        pos.x = at.x
        pos.y = at.y

    def _make_entity(self, templates: MutableSequence[str]) -> Entity:
        """Make a new entity."""
        components = []
        for template in templates:
            # Don't catch KeyError here... let it fail
            data = self._loader.data[self._data_key][template]
            for component_type, component_data in data['Components'].items():
                # find the actual class
                try:
                    component_class = get_component_class(component_type)
                except (AttributeError, ModuleNotFoundError) as exc:
                    raise FactoryException(
                        f'Error in {self._data_key}.{template}: {component_type}: {exc}')
                try:
                    kwargs = self._convert_data(component_data)
                except (AttributeError, KeyError) as exc:
                    raise FactoryException(
                        f'Error in {self._data_key}.{template}: {component_data}: {repr(exc)}')
                try:
                    validate_kwargs(kwargs)
                except (TypeError, ValueError) as exc:
                    raise FactoryException(f'Error in {self._data_key}.{template}: {exc}')
                try:
                    components.append(component_class(**kwargs))
                except TypeError as exc:
                    raise FactoryException(f'Error in {self._data_key}.{template}: {exc}')
        return self._world.create_entity(*components)

    def _convert_data(self, data: Mapping) -> dict:
        """Convert data to globals."""
        new_data = {}
        for key, value in data.items():
            new_data[key] = value
            converted = convert_datum(value)
            if converted is not None:
                new_data[key] = converted
            else:
                try:
                    if value.startswith(ON_CREATE):
                        converted_func = parse(value[len(ON_CREATE):], self._rng)
                        if converted_func is not None:
                            new_data[key] = converted_func()
                except AttributeError:
                    pass
        return new_data


class PlayerFactory(BaseEntityFactory):
    """Factory for creating Player entities."""

    def __init__(self, loader: DataLoader, world: World) -> None:
        super().__init__(loader, world)
        self._rng = RNGCache.get('PlayerFactory')
        self._data_key = 'assemblage.player'

    def make(self, templates: MutableSequence[str]) -> Entity:
        """Make a player entity."""
        if 'BasicPlayer' not in templates:
            templates.insert(0, 'BasicPlayer')
        ent = self._make_entity(templates)
        self._world.players.add(ent)
        # TODO: should placement be elsewhere?
        self.place_entity(ent, self._rng.choice(self._world.map.spawns_player()))
        return ent


class EnemyFactory(BaseEntityFactory):
    """Factory for creating Enemy entities."""

    def __init__(self, loader: DataLoader, world: World) -> None:
        super().__init__(loader, world)
        self._rng = RNGCache.get('EnemyFactory')
        self._data_key = 'assemblage.enemy'

    def make(self, templates: MutableSequence[str]) -> Entity:
        """Make a player entity."""
        if 'BasicEnemy' not in templates:
            templates.insert(0, 'BasicEnemy')
        ent = self._make_entity(templates)
        # TODO: should placement be elsewhere?
        self.place_entity(ent, self._rng.choice(self._world.map.spawns_enemy()))
        return ent

    def place_entity(self, ent: Entity, at: Point) -> None:
        """Place an enemy on the map where no other entities are."""
        tries = 10000
        while tries and self._world.get_entity_at_position(at.x, at.y):
            tries -= 1
            at = self._rng.choice(self._world.map.spawns_enemy())
        if tries > 0:
            super().place_entity(ent, at)
        else:
            raise FactoryException(f'Could not place enemy entity: {ent}')


class ItemFactory(BaseEntityFactory):
    """Factory for creating Item entities."""

    def __init__(self, loader: DataLoader, world: World) -> None:
        super().__init__(loader, world)
        self._rng = RNGCache.get('ItemFactory')
        self._data_key = 'assemblage.item'

    def make(self, templates: MutableSequence[str]) -> Entity:
        """Make a player entity."""
        if 'BasicItem' not in templates:
            templates.insert(0, 'BasicItem')
        ent = self._make_entity(templates)
        # TODO: should placement be elsewhere?
        self.place_entity(ent, self._rng.choice(self._world.map.spawns_item()))
        return ent
