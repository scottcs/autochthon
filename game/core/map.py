"""Game map."""
from __future__ import annotations

import enum
import typing

import numpy as np
import tcod.map

import game.const.palette
import game.utils.geometry
import game.utils.random
import game.utils.render

LOOP_TRIES = 10000
MAP_BITS = (
    "explored",
    "spawnable_player",
    "spawnable_enemy",
    "spawnable_item",
    "contains_player",
    "contains_enemy",
    "contains_item",
    "alt_tile_1",
    "alt_tile_2",
    "alt_tile_3",
)
# TODO: interaction layer? others?


class TileType(enum.Enum):
    """Tile types."""

    floor = enum.auto()
    wall_v = enum.auto()
    wall_h = enum.auto()


class Map(tcod.map.Map):
    """Game map."""

    def __init__(
        self,
        width: int,
        height: int,
        seed: typing.Optional[str] = None,
        config: typing.Optional[typing.Mapping] = None,
    ) -> None:
        """Create a new map with the given dimensions."""
        super().__init__(width, height)
        self._iter_x: int = 0
        self._iter_y: int = 0
        self.config = config or {}
        self._rng = game.utils.random.RNGCache.get(seed)
        self._buffer2: np.array = np.zeros((height, width, len(MAP_BITS)), dtype=np.bool_)

    @property
    def explored(self) -> np.array:
        """Array of cells that have been explored."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index("explored")]
        return buffer

    @property
    def spawnable_player(self) -> np.array:
        """Array of cells that can spawn a player."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index("spawnable_player")]
        return buffer

    def spawnable_player_list(self) -> typing.List[game.utils.geometry.Point]:
        """Return a list of only spawnable player coordinates."""
        return [
            game.utils.geometry.Point(int(x), int(y))
            for y, x in np.transpose(self.spawnable_player.nonzero())
        ]

    @property
    def spawnable_enemy(self) -> np.array:
        """Array of cells that can spawn enemies."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index("spawnable_enemy")]
        return buffer

    def spawnable_enemy_list(self) -> typing.List[game.utils.geometry.Point]:
        """Return a list of only spawnable enemy coordinates."""
        return [
            game.utils.geometry.Point(int(x), int(y))
            for y, x in np.transpose(self.spawnable_enemy.nonzero())
        ]

    @property
    def spawnable_item(self) -> np.array:
        """Array of cells that can spawn items."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index("spawnable_item")]
        return buffer

    def spawnable_item_list(self) -> typing.List[game.utils.geometry.Point]:
        """Return a list of only spawnable item coordinates."""
        return [
            game.utils.geometry.Point(int(x), int(y))
            for y, x in np.transpose(self.spawnable_item.nonzero())
        ]

    @property
    def contains_player(self) -> np.array:
        """Array of cells that contain players."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index("contains_player")]
        return buffer

    def contains_player_list(self) -> typing.List[game.utils.geometry.Point]:
        """Return a list of only coordinates occupied by players."""
        return [
            game.utils.geometry.Point(int(x), int(y))
            for y, x in np.transpose(self.contains_player.nonzero())
        ]

    @property
    def contains_enemy(self) -> np.array:
        """Array of cells that contain enemies."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index("contains_enemy")]
        return buffer

    def contains_enemy_list(self) -> typing.List[game.utils.geometry.Point]:
        """Return a list of only coordinates occupied by enemies."""
        return [
            game.utils.geometry.Point(int(x), int(y))
            for y, x in np.transpose(self.contains_enemy.nonzero())
        ]

    @property
    def contains_item(self) -> np.array:
        """Array of cells that can spawn items."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index("contains_item")]
        return buffer

    def contains_item_list(self) -> typing.List[game.utils.geometry.Point]:
        """Return a list of only coordinates occupied by items."""
        return [
            game.utils.geometry.Point(int(x), int(y))
            for y, x in np.transpose(self.contains_item.nonzero())
        ]

    @property
    def alt_tile_1(self) -> np.array:
        """Array of cells that the alt tile 1 bit set."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index("alt_tile_1")]
        return buffer

    @property
    def alt_tile_2(self) -> np.array:
        """Array of cells that the alt tile 2 bit set."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index("alt_tile_2")]
        return buffer

    @property
    def alt_tile_3(self) -> np.array:
        """Array of cells that the alt tile 3 bit set."""
        buffer: np.array = self._buffer2[:, :, MAP_BITS.index("alt_tile_3")]
        return buffer

    def create(self) -> None:
        """Create the map using the map's algorithm."""
        raise NotImplementedError("This class must be subclassed.")

    def find_player_spawn(
        self, at: typing.Optional[game.utils.geometry.Point] = None
    ) -> typing.Optional[game.utils.geometry.Point]:
        """Find an open player spawn point."""
        if at is None:
            at = self._rng.choice(self.spawnable_player_list())
        tries = LOOP_TRIES
        while tries and self.contains_player[at.y, at.x] or self.contains_enemy[at.y, at.x]:
            tries -= 1
            at = self._rng.choice(self.spawnable_player_list())
        if tries > 0:
            return at
        return None

    def find_enemy_spawn(
        self, at: typing.Optional[game.utils.geometry.Point] = None
    ) -> typing.Optional[game.utils.geometry.Point]:
        """Find an open enemy spawn point."""
        if at is None:
            at = self._rng.choice(self.spawnable_enemy_list())
        tries = LOOP_TRIES
        while tries and self.contains_player[at.y, at.x] or self.contains_enemy[at.y, at.x]:
            tries -= 1
            at = self._rng.choice(self.spawnable_enemy_list())
        if tries > 0:
            return at
        return None

    def find_item_spawn(
        self, at: typing.Optional[game.utils.geometry.Point] = None
    ) -> typing.Optional[game.utils.geometry.Point]:
        """Find an open item spawn point."""
        if at is None:
            at = self._rng.choice(self.spawnable_item_list())
        tries = LOOP_TRIES
        while tries and self.contains_item[at.y, at.x]:
            tries -= 1
            at = self._rng.choice(self.spawnable_item_list())
        if tries > 0:
            return at
        return None

    def _calculate_tile_type(self, y: int, x: int) -> TileType:
        if self.walkable[y, x]:
            return TileType.floor
        try:
            if self.walkable[y + 1, x]:
                return TileType.wall_h
        except IndexError:
            pass
        return TileType.wall_v

    def _tile_id_from_type(self, tile_type: TileType, y: int, x: int) -> int:
        # TODO: move these definitions to a data file/change based on map "theme"
        suffixes = "ABCD"
        idx = 0
        if self.alt_tile_3[y, x]:
            idx += 1
        if self.alt_tile_2[y, x]:
            idx += 1
        if self.alt_tile_1[y, x]:
            idx += 1
        if tile_type == TileType.wall_v:
            return game.utils.render.TileCache.id_from_name(
                "terrain_wallAVertical" + suffixes[idx]
            )
        elif tile_type == TileType.wall_h:
            return game.utils.render.TileCache.id_from_name(
                "terrain_wallAHorizontal" + suffixes[idx]
            )
        elif tile_type == TileType.floor:
            return game.utils.render.TileCache.id_from_name("terrain_floorOverlay" + suffixes[idx])
        else:
            raise RuntimeError(f"Unknown tile type: {tile_type}")

    @staticmethod
    def _tile_color_from_type(tile_type: TileType) -> int:
        # TODO: move these definitions to a data file/change based on map "theme"
        if tile_type == TileType.wall_v:
            return game.const.palette.Base.brown
        elif tile_type == TileType.wall_h:
            return game.const.palette.Base.brown
        elif tile_type == TileType.floor:
            return game.const.palette.Base.dark_grey
        else:
            raise RuntimeError(f"Unknown tile type: {tile_type}")

    def __iter__(self) -> Map:
        self._iter_y = -1
        self._iter_x = 0
        return self

    def __next__(self) -> typing.Tuple[int, int]:
        self._iter_y += 1
        if self._iter_y == self.height:
            self._iter_y = 0
            self._iter_x += 1
        if self._iter_x == self.width:
            raise StopIteration
        return self._iter_y, self._iter_x

    def get_tile(self, y: int, x: int) -> typing.Tuple[int, int]:
        """Determine the tile id and color at the given coordinate."""
        tile_type = self._calculate_tile_type(y, x)
        return self._tile_id_from_type(tile_type, y, x), self._tile_color_from_type(tile_type)

    def __len__(self) -> int:
        return self.width * self.height


class ClassicMap(Map):
    """Classic rogue-style map."""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.max_rooms: int = self.config.get("max_rooms", 50)
        self.room_min_size: int = self.config.get("room_min_size", 5)
        self.room_max_size: int = self.config.get("room_max_size", 20)

    def create_room(self, room: game.utils.geometry.Rect) -> None:
        """Create a new room in the map at the given coordinates.

        NOTE: a `room` includes wall tiles!

        """
        for x in range(room.p1.x, room.p2.x + 1):
            for y in range(room.p1.y, room.p2.y + 1):
                if room.p1.x < x < room.p2.x and room.p1.y < y < room.p2.y:
                    self.walkable[y, x] = True
                    self.transparent[y, x] = True
                    self.spawnable_enemy[y, x] = True
                    self.spawnable_item[y, x] = True
                if self._rng.percent(0.01):
                    self.alt_tile_1[y, x] = True
                if self._rng.percent(0.01):
                    self.alt_tile_2[y, x] = True
                if self._rng.percent(0.01):
                    self.alt_tile_3[y, x] = True

    def create_h_tunnel(self, x1: int, x2: int, y: int) -> None:
        """Create a single-width horizontal tunnel from x1 to x2 along y."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.walkable[y, x] = True
            self.transparent[y, x] = True
            for yy in range(y - 1, y + 2):
                try:
                    if self._rng.percent(0.01):
                        self.alt_tile_1[yy, x] = True
                    if self._rng.percent(0.02):
                        self.alt_tile_2[yy, x] = True
                    if self._rng.percent(0.03):
                        self.alt_tile_3[yy, x] = True
                except IndexError:
                    pass

    def create_v_tunnel(self, y1: int, y2: int, x: int) -> None:
        """Create a single-width vertical tunnel from y1 to y2 along x."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.walkable[y, x] = True
            self.transparent[y, x] = True
            for xx in range(x - 1, x + 2):
                try:
                    if self._rng.percent(0.01):
                        self.alt_tile_1[y, xx] = True
                    if self._rng.percent(0.02):
                        self.alt_tile_2[y, xx] = True
                    if self._rng.percent(0.03):
                        self.alt_tile_3[y, xx] = True
                except IndexError:
                    pass

    def create(self) -> None:
        """Create the map."""
        rooms: typing.List[game.utils.geometry.Rect] = []

        for _ in range(self.max_rooms):
            w: int = self._rng.rand(self.room_min_size, self.room_max_size)
            h: int = self._rng.rand(self.room_min_size, self.room_max_size)
            x: int = self._rng.rand(self.width - w - 1)
            y: int = self._rng.rand(self.height - h - 1)

            new_room: game.utils.geometry.Rect = game.utils.geometry.Rect(x, y, w, h)
            new_center: game.utils.geometry.Point = new_room.center

            for other_room in rooms:
                if new_room.intersects(other_room):
                    break
            else:  # no intersections, so this room is valid
                self.create_room(new_room)

                if len(rooms) == 0:  # first room
                    self.spawnable_player[new_room.center.y, new_room.center.x] = True
                else:
                    prev_center: game.utils.geometry.Point = rooms[-1].center
                    if self._rng.coin():
                        self.create_h_tunnel(prev_center.x, new_center.x, prev_center.y)
                        self.create_v_tunnel(prev_center.y, new_center.y, new_center.x)
                    else:
                        self.create_v_tunnel(prev_center.y, new_center.y, prev_center.x)
                        self.create_h_tunnel(prev_center.x, new_center.x, new_center.y)
                rooms.append(new_room)
