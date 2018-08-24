"""Factory utilities."""
import logging
from typing import Any, List

from game.component.movement import Position
from game.dataloader import DataLoader
from game.types import Entity
from game.utils.geometry import Point
from game.utils.render import TileCache
from game.world import World

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class FactoryException(Exception):
    """Factory exceptions."""


def _convert_data(data: dict) -> dict:
    """Convert data to globals."""
    for key, value in data.items():
        try:
            class_type, attr = value.split('.')
        except (ValueError, AttributeError):
            # the value does not have two parts separated by '.', or is not a string
            continue

        if class_type == 'Palette':
            from gamedata.palette import Palette
            data[key] = getattr(Palette, attr)
        elif class_type == 'RenderLayer':
            from game.types import RenderLayer
            data[key] = getattr(RenderLayer, attr)
        else:
            data[key] = getattr(globals()[class_type], attr)
    return data


def _get_component_class(class_substring: str) -> Any:
    """Get a component class from a substring like `attack.AttackCostModifier`."""
    component_group, component_class = class_substring.split('.')
    mod_name = f'game.component.{component_group}'
    _tmp = __import__(mod_name, globals=globals(), locals=locals(), fromlist=[component_class])
    return getattr(_tmp, component_class)


def _validate_kwargs(kwargs: dict) -> None:
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
                component_class = _get_component_class(component_type)
            except (AttributeError, ModuleNotFoundError) as exc:
                raise FactoryException(f'Error in {data_key}.{template}: {component_type}: {exc}')
            try:
                kwargs = _convert_data(component_data)
            except (AttributeError, KeyError) as exc:
                raise FactoryException(
                    f'Error in {data_key}.{template}: {component_data}: {repr(exc)}')
            try:
                _validate_kwargs(kwargs)
            except Exception as exc:
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


def make_player(loader: DataLoader, world: World, start: Point, templates: List[str]) -> Entity:
    """Make a player and add it to the world."""
    if 'BasicPlayer' not in templates:
        templates.insert(0, 'BasicPlayer')
    ent = make_entity(loader, world, 'entities.player', start, templates)
    world.players.add(ent)
    return ent


def make_enemy(loader: DataLoader, world: World, start: Point, templates: List[str]) -> Entity:
    """Make an enemy and add it to the world."""
    if 'BasicEnemy' not in templates:
        templates.insert(0, 'BasicEnemy')
    return make_entity(loader, world, 'entities.enemy', start, templates)
