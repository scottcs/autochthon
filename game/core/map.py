"""Game map."""
from __future__ import annotations
from random import randint
from typing import List, Optional, Tuple, NamedTuple

import esper
import numpy as np
import tcod.map

from game.utils.geometry import Rect, Point
from game.utils.random import coin_flip
from gamedata.palette import Palette

MAP_BITS = ('explored', 'spawnable_player', 'spawnable_enemy', 'spawnable_item')
# TODO: item layer? interaction layer? enemy layer? etc?


class MapCell(NamedTuple):
    """Map cell."""
    x: int = 0
    y: int = 0
    transparent: bool = False
    walkable: bool = False
    fov: bool = False
    explored: bool = False
    spawnable_player: bool = False
    spawnable_enemy: bool = False
    spawnable_item: bool = False


class Map(tcod.map.Map):
    """Game map."""

    def __init__(self, width: int, height: int, world: esper.World) -> None:
        """Create a new map with the given dimensions."""
        super().__init__(width, height)
        self.world: esper.World = world
        self._iter_x: int = 0
        self._iter_y: int = 0
        self._buffer2: np.array = np.zeros((height, width, len(MAP_BITS)), dtype=np.bool_)

        # TODO: make these more dynamic
        self.floor_tile_id = 220
        self.floor_color: int = Palette.dark_grey
        self.wall_tile_id = 234
        self.wall_color: int = Palette.brown

    @property
    def explored(self) -> np.array:
        """Array of cells that have been explored."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index('explored')]
        return buffer

    @property
    def spawnable_player(self) -> np.array:
        """Array of cells that can spawn a player."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index('spawnable_player')]
        return buffer

    def spawns_player(self) -> List[Point]:
        """Return a list of only spawnable player coordinates."""
        return [Point(int(x), int(y)) for y, x in np.transpose(self.spawnable_player.nonzero())]

    @property
    def spawnable_enemy(self) -> np.array:
        """Array of cells that can spawn enemies."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index('spawnable_enemy')]
        return buffer

    def spawns_enemy(self) -> List[Point]:
        """Return a list of only spawnable enemy coordinates."""
        return [Point(int(x), int(y)) for y, x in np.transpose(self.spawnable_enemy.nonzero())]

    @property
    def spawnable_item(self) -> np.array:
        """Array of cells that can spawn items."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index('spawnable_item')]
        return buffer

    def spawns_item(self) -> List[Point]:
        """Return a list of only spawnable item coordinates."""
        return [Point(int(x), int(y)) for y, x in np.transpose(self.spawnable_item.nonzero())]

    def create(self) -> None:
        """Create the map using the map's algorithm."""
        raise NotImplementedError('This class must be subclassed.')

    def __iter__(self) -> Map:
        self._iter_x: int = 0
        self._iter_y: int = 0
        return self

    def __next__(self) -> MapCell:
        try:
            cell: MapCell = self[self._iter_x, self._iter_y]
        except IndexError:
            raise StopIteration
        self._iter_y += 1
        if self._iter_y == self.height:
            self._iter_y = 0
            self._iter_x += 1
        return cell

    def __getitem__(self, item: Tuple[int, int]) -> MapCell:
        x, y = item
        try:
            return MapCell(
                x,
                y,
                self.transparent[y, x],
                self.walkable[y, x],
                self.fov[y, x],
                self.explored[y, x],
                self.spawnable_player[y, x],
                self.spawnable_enemy[y, x],
                self.spawnable_item[y, x],
            )
        except IndexError:
            raise IndexError(f'Location ({x}, {y}) in map not found.')

    def __len__(self) -> int:
        return self.width * self.height


class ClassicMap(Map):
    """Classic rogue-style map."""

    def __init__(self, width: int, height: int, world: esper.World,
                 config: Optional[dict]=None) -> None:
        super().__init__(width, height, world)
        config = config or {}
        self.max_rooms: int = config.get('max_rooms', 50)
        self.room_min_size: int = config.get('room_min_size', 5)
        self.room_max_size: int = config.get('room_max_size', 20)

    def create_room(self, room: Rect) -> None:
        """Create a new room in the map at the given coordinates."""
        for x in range(room.p1.x + 1, room.p2.x):
            for y in range(room.p1.y + 1, room.p2.y):
                self.walkable[y, x] = True
                self.transparent[y, x] = True
                self.spawnable_enemy[y, x] = True
                self.spawnable_item[y, x] = True

    def create_h_tunnel(self, x1: int, x2: int, y: int) -> None:
        """Create a single-width horizontal tunnel from x1 to x2 along y."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.walkable[y, x] = True
            self.transparent[y, x] = True

    def create_v_tunnel(self, y1: int, y2: int, x: int) -> None:
        """Create a single-width vertical tunnel from y1 to y2 along x."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.walkable[y, x] = True
            self.transparent[y, x] = True

    def create(self) -> None:
        """Create the map."""
        rooms: List[Rect] = []

        for r in range(self.max_rooms):
            w: int = randint(self.room_min_size, self.room_max_size)
            h: int = randint(self.room_min_size, self.room_max_size)
            x: int = randint(0, self.width - w - 1)
            y: int = randint(0, self.height - h - 1)

            new_room: Rect = Rect(x, y, w, h)
            new_center: Point = new_room.center

            for other_room in rooms:
                if new_room.intersects(other_room):
                    break
            else:  # no intersections, so this room is valid
                self.create_room(new_room)

                if len(rooms) == 0:  # first room
                    self.spawnable_player[new_room.center.y, new_room.center.x] = True
                else:
                    prev_center: Point = rooms[-1].center
                    if coin_flip():
                        self.create_h_tunnel(prev_center.x, new_center.x, prev_center.y)
                        self.create_v_tunnel(prev_center.y, new_center.y, new_center.x)
                    else:
                        self.create_v_tunnel(prev_center.y, new_center.y, prev_center.x)
                        self.create_h_tunnel(prev_center.x, new_center.x, new_center.y)
                rooms.append(new_room)
