"""Factory utilities."""
import logging
from typing import Any, List

from game.component.movement import Position
from game.utils.dataloader import DataLoader
from game.types import Entity
from game.utils.geometry import Point
from game.utils.random import parse, RNGCache
from game.utils.render import TileCache
from game.core.world import World

ON_CREATE = '=='

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class FactoryException(Exception):
    """Factory exceptions."""


def _convert_data(data: dict) -> dict:
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
                    converted_func = parse(value[len(ON_CREATE):])
                    if converted_func is not None:
                        new_data[key] = converted_func()
            except AttributeError:
                pass
    return new_data


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


def validate_kwargs(kwargs: dict) -> None:
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


def make_entity(loader: DataLoader, world: World, data_key: str,
                start: Point, templates: List[str]) -> Entity:
    """Make a player and add it to the world."""
    components = []
    for template in templates:
        # Don't catch KeyError here... let it fail
        data = loader.data[data_key][template]
        for component_type, component_data in data['Components'].items():
            # find the actual class
            try:
                component_class = get_component_class(component_type)
            except (AttributeError, ModuleNotFoundError) as exc:
                raise FactoryException(f'Error in {data_key}.{template}: {component_type}: {exc}')
            try:
                kwargs = _convert_data(component_data)
            except (AttributeError, KeyError) as exc:
                raise FactoryException(
                    f'Error in {data_key}.{template}: {component_data}: {repr(exc)}')
            try:
                validate_kwargs(kwargs)
            except (TypeError, ValueError) as exc:
                raise FactoryException(f'Error in {data_key}.{template}: {exc}')
            try:
                components.append(component_class(**kwargs))
            except TypeError as exc:
                raise FactoryException(f'Error in {data_key}.{template}: {exc}')
    ent = world.create_entity(*components)
    pos = world.component_for_entity(ent, Position)
    pos.x = start.x
    pos.y = start.y
    return ent


def make_player(loader: DataLoader, world: World, templates: List[str]) -> Entity:
    """Make a player and add it to the world."""
    rng = RNGCache.get('PlayerFactory')
    if 'BasicPlayer' not in templates:
        templates.insert(0, 'BasicPlayer')
    pos = rng.choice(world.map.spawns_player())
    ent = make_entity(loader, world, 'assemblage.player', pos, templates)
    world.players.add(ent)
    return ent


def make_enemy(loader: DataLoader, world: World, templates: List[str]) -> Entity:
    """Make an enemy and add it to the world."""
    rng = RNGCache.get('EnemyFactory')
    if 'BasicEnemy' not in templates:
        templates.insert(0, 'BasicEnemy')
    pos = rng.choice(world.map.spawns_enemy())
    return make_entity(loader, world, 'assemblage.enemy', pos, templates)


def make_item(loader: DataLoader, world: World, templates: List[str]) -> Entity:
    """Make an item and add it to the world."""
    rng = RNGCache.get('ItemFactory')
    if 'BasicItem' not in templates:
        templates.insert(0, 'BasicItem')
    pos = rng.choice(world.map.spawns_item())
    return make_entity(loader, world, 'assemblage.item', pos, templates)
