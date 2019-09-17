"""Factory utilities."""
import logging
import pydoc
import typing

import game.component.movement
import game.constants.palette
import game.core.world
import game.types
import game.utils.dataloader
import game.utils.geometry
import game.utils.random
import game.utils.render

ON_CREATE = "=="

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class FactoryException(Exception):
    """Factory exceptions."""


def convert_datum(value: typing.Any) -> typing.Any:
    """Convert a data value to a global class.attribute value, if possible."""
    try:
        class_type, attr = value.split(".")
    except (ValueError, AttributeError):
        # the value does not have two parts separated by '.', or is not a string
        return None

    if class_type == "Palette":
        result = getattr(game.constants.palette.Base, attr)
    else:
        imported = pydoc.locate(f"game.types.{class_type}")
        if imported:
            result = getattr(imported, attr)
        else:
            # allow exception to be raised here if it doesn't exist
            result = getattr(globals()[class_type], attr)
    return result


def get_component_class(class_substring: str) -> typing.Any:
    """Get a component class from a substring like `attack.AttackHitModifier`."""
    component_group, component_class = class_substring.split(".")
    mod_name = f"game.component.{component_group}"
    _tmp = __import__(mod_name, globals=globals(), locals=locals(), fromlist=[component_class])
    return getattr(_tmp, component_class)


def validate_kwargs(kwargs: typing.MutableMapping) -> None:
    """Validate keyword arguments for components."""
    for key, value in kwargs.items():
        if value is None:
            raise TypeError(f'Value for "{key}" must be specified.')
        if key == "tile_id":
            try:
                value = int(value)
            except ValueError:
                id_ = game.utils.render.TileCache.id_from_name(value)
                if id_ is None:
                    raise ValueError(f"Cannot find tile id for {value}")
                value = int(id_)
            kwargs[key] = value


class BaseEntityFactory:
    """Entity Factory."""

    def __init__(
        self, loader: game.utils.dataloader.DataLoader, world: game.core.world.World
    ) -> None:
        self._loader: game.utils.dataloader.DataLoader = loader
        self._world: game.core.world.World = world
        self._rng: typing.Optional[game.utils.random.GameRNG] = None
        self._data_key: typing.Optional[str] = None

    def make(self, templates: typing.MutableSequence[str]) -> game.types.Entity:
        """Make an entity."""
        raise NotImplementedError("Must implement in child class.")

    def place_entity(self, ent: game.types.Entity, at: game.utils.geometry.Point) -> None:
        """Place an entity at the given position in the world."""
        pos = self._world.component_for_entity(ent, game.component.movement.Position)
        pos.x = at.x
        pos.y = at.y

    def _make_entity(self, templates: typing.MutableSequence[str]) -> game.types.Entity:
        """Make a new entity."""
        components = []
        for template in templates:
            # Don't catch KeyError here... let it fail
            data = self._loader.data[self._data_key][template]
            for component_type, component_data in data["Components"].items():
                # find the actual class
                try:
                    component_class = get_component_class(component_type)
                except (AttributeError, ModuleNotFoundError) as exc:
                    raise FactoryException(
                        f"Error in {self._data_key}.{template}: {component_type}: {exc}"
                    )
                try:
                    kwargs = self._convert_data(component_data)
                except (AttributeError, KeyError) as exc:
                    raise FactoryException(
                        f"Error in {self._data_key}.{template}: {component_data}: {repr(exc)}"
                    )
                try:
                    validate_kwargs(kwargs)
                except (TypeError, ValueError) as exc:
                    raise FactoryException(f"Error in {self._data_key}.{template}: {exc}")
                try:
                    components.append(component_class(**kwargs))
                except TypeError as exc:
                    raise FactoryException(f"Error in {self._data_key}.{template}: {exc}")
        return self._world.create_entity(*components)

    def _convert_data(self, data: typing.Mapping) -> dict:
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
                        if self._rng:
                            converted_func = game.utils.random.parse(
                                value[len(ON_CREATE) :], self._rng
                            )
                            if converted_func is not None:
                                new_data[key] = converted_func()
                except AttributeError:
                    pass
        return new_data


class Player(BaseEntityFactory):
    """Factory for creating Player entities."""

    def __init__(
        self, loader: game.utils.dataloader.DataLoader, world: game.core.world.World
    ) -> None:
        super().__init__(loader, world)
        self._rng: game.utils.random.GameRNG = game.utils.random.RNGCache.get("PlayerFactory")
        self._data_key: str = "assemblage.player"

    def make(self, templates: typing.MutableSequence[str]) -> game.types.Entity:
        """Make a player entity."""
        if not self._world.map:
            raise FactoryException("There is no map!")
        if "BasicPlayer" not in templates:
            templates.insert(0, "BasicPlayer")
        ent = self._make_entity(templates)
        self._world.players.add(ent)
        loc: typing.Optional[game.utils.geometry.Point] = self._world.map.find_player_spawn()
        if loc is None:
            raise FactoryException(f"Could not place player entity: {ent}")
        else:
            self.place_entity(ent, loc)
            self._world.map.contains_player[loc.y, loc.x] = True
        return ent


class Enemy(BaseEntityFactory):
    """Factory for creating Enemy entities."""

    def __init__(
        self, loader: game.utils.dataloader.DataLoader, world: game.core.world.World
    ) -> None:
        super().__init__(loader, world)
        self._rng: game.utils.random.GameRNG = game.utils.random.RNGCache.get("EnemyFactory")
        self._data_key: str = "assemblage.enemy"

    def make(self, templates: typing.MutableSequence[str]) -> game.types.Entity:
        """Make a player entity."""
        if not self._world.map:
            raise FactoryException("There is no map!")
        if "BasicEnemy" not in templates:
            templates.insert(0, "BasicEnemy")
        ent = self._make_entity(templates)
        loc: typing.Optional[game.utils.geometry.Point] = self._world.map.find_enemy_spawn()
        if loc is None:
            raise FactoryException(f"Could not place enemy entity: {ent}")
        else:
            self.place_entity(ent, loc)
            self._world.map.contains_enemy[loc.y, loc.x] = True
        return ent


class Item(BaseEntityFactory):
    """Factory for creating Item entities."""

    def __init__(
        self, loader: game.utils.dataloader.DataLoader, world: game.core.world.World
    ) -> None:
        super().__init__(loader, world)
        self._rng: game.utils.random.GameRNG = game.utils.random.RNGCache.get("ItemFactory")
        self._data_key: str = "assemblage.item"

    def make(self, templates: typing.MutableSequence[str]) -> game.types.Entity:
        """Make a player entity."""
        if not self._world.map:
            raise FactoryException("There is no map!")
        if "BasicItem" not in templates:
            templates.insert(0, "BasicItem")
        ent = self._make_entity(templates)
        loc: typing.Optional[game.utils.geometry.Point] = self._world.map.find_item_spawn()
        if loc is None:
            raise FactoryException(f"Could not place item entity: {ent}")
        else:
            self.place_entity(ent, loc)
            self._world.map.contains_item[loc.y, loc.x] = True
        return ent
