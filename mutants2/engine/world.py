from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Set, Optional, Iterable

from .senses import Direction
from . import monsters as monsters_mod
Coordinate = Tuple[int, int]


@dataclass
class Cell:
    x: int
    y: int


class Grid:
    """A simple 4-neighbour grid."""

    def __init__(self, width: int, height: int, adj: Dict[Coordinate, Set[Direction]]):
        self.width = width
        self.height = height
        self.adj = adj

    def is_walkable(self, x: int, y: int) -> bool:
        return (x, y) in self.adj

    def neighbors(self, x: int, y: int) -> Dict[Direction, Coordinate]:
        dirs = {
            'north': (0, 1),
            'south': (0, -1),
            'east': (1, 0),
            'west': (-1, 0),
        }
        result: Dict[Direction, Coordinate] = {}
        if not self.is_walkable(x, y):
            return result
        for name, (dx, dy) in dirs.items():
            nx, ny = x + dx, y + dy
            if name in self.adj[(x, y)] and 0 <= nx < self.width and 0 <= ny < self.height:
                result[name] = (nx, ny)
        return result


@dataclass
class Year:
    value: int
    grid: Grid


class World:
    def __init__(
        self,
        ground: Optional[Dict[Tuple[int, int, int], str]] = None,
        seeded_years: Optional[Set[int]] = None,
        monsters: Optional[Dict[Tuple[int, int, int], dict]] = None,
        *,
        global_seed: int | None = None,
    ):
        self.years: Dict[int, Year] = {}
        self.ground: Dict[Tuple[int, int, int], str] = ground or {}
        self.seeded_years: Set[int] = set(seeded_years or [])
        self._monsters: Dict[Tuple[int, int, int], dict] = {}
        if monsters:
            for coord, data in monsters.items():
                if isinstance(data, dict):
                    key = data.get("key")
                    hp = data.get("hp")
                else:
                    key = data
                    hp = None
                if key is None:
                    continue
                base = monsters_mod.REGISTRY[key].base_hp
                self._monsters[coord] = {"key": key, "hp": int(hp) if hp is not None else base}
        if global_seed is None:
            from . import gen

            global_seed = gen.SEED
        self.global_seed = global_seed

    def ground_item(self, year: int, x: int, y: int) -> Optional[str]:
        return self.ground.get((year, x, y))

    def set_ground_item(self, year: int, x: int, y: int, item_key: Optional[str]) -> None:
        key = (year, x, y)
        if item_key is None:
            self.ground.pop(key, None)
        else:
            self.ground[key] = item_key

    # Helpers for daily top-up -------------------------------------------------

    def known_years(self) -> list[int]:
        yrs = set(self.years.keys()) | {y for (y, _, _) in self.ground.keys()} | set(self.seeded_years)
        return sorted(yrs)

    def walkable_coords(self, year: int) -> Iterable[Tuple[int, int]]:
        grid = self.year(year).grid
        for x in range(grid.width):
            for y in range(grid.height):
                if grid.is_walkable(x, y):
                    yield (x, y)

    def item_at(self, year: int, x: int, y: int) -> Optional[str]:
        return self.ground_item(year, x, y)

    def place_item(self, year: int, x: int, y: int, item_key: str) -> None:
        self.set_ground_item(year, x, y, item_key)

    def ground_items_count(self, year: int) -> int:
        return sum(1 for (yr, _, _) in self.ground.keys() if yr == year)

    @property
    def monsters(self) -> Dict[Tuple[int, int, int], dict]:
        return self._monsters

    # Monsters -----------------------------------------------------------------

    def monsters_in_year(self, year: int) -> dict[tuple[int, int], str]:
        return {
            (x, y): data["key"]
            for (yr, x, y), data in self._monsters.items()
            if yr == year
        }

    def has_monster(self, year: int, x: int, y: int) -> bool:
        return (year, x, y) in self._monsters

    def monster_here(self, year: int, x: int, y: int) -> dict | None:
        return self._monsters.get((year, x, y))

    def place_monster(self, year: int, x: int, y: int, key: str) -> bool:
        coord = (year, x, y)
        if coord in self._monsters:
            return False
        base = monsters_mod.REGISTRY[key].base_hp
        self._monsters[coord] = {"key": key, "hp": base}
        return True

    def ensure_monster(self, year: int, x: int, y: int, key: str) -> None:
        base = monsters_mod.REGISTRY[key].base_hp
        self._monsters[(year, x, y)] = {"key": key, "hp": base}

    def damage_monster(self, year: int, x: int, y: int, dmg: int) -> bool:
        coord = (year, x, y)
        m = self._monsters.get(coord)
        if not m:
            return False
        m["hp"] = max(0, m["hp"] - max(0, dmg))
        if m["hp"] <= 0:
            self._monsters.pop(coord, None)
            return True
        return False

    def remove_monster(self, year: int, x: int, y: int) -> bool:
        coord = (year, x, y)
        return self._monsters.pop(coord, None) is not None

    def monster_count(self, year: int) -> int:
        return sum(1 for (yr, _, _), _ in self._monsters.items() if yr == year)

    _DIRS: dict[Direction, tuple[int, int]] = {
        "north": (0, 1),
        "south": (0, -1),
        "east": (1, 0),
        "west": (-1, 0),
    }

    def is_open(self, year: int, x: int, y: int, direction: Direction) -> bool:
        """Return ``True`` if an open passage exists from ``(x, y)`` to ``direction``."""
        grid = self.year(year).grid
        return direction in grid.neighbors(x, y)

    def step(self, x: int, y: int, direction: Direction) -> tuple[int, int]:
        """Return coordinates stepped one tile in ``direction`` from ``(x, y)``."""
        dx, dy = self._DIRS[direction]
        return x + dx, y + dy

    def nearest_monster(
        self, year: int, x: int, y: int, max_dist: int = 4
    ) -> tuple[int, int, int] | None:
        hit: tuple[int, int, int] | None = None
        for (yr, mx, my), _data in self._monsters.items():
            if yr != year:
                continue
            dist = abs(mx - x) + abs(my - y)
            if dist > max_dist:
                continue
            if hit is None or dist < hit[2]:
                hit = (mx - x, my - y, dist)
        return hit

    def year(self, value: int) -> Year:
        """Return the :class:`Year` for ``value`` generating it if needed."""
        if value not in self.years:
            from . import gen

            grid = gen.generate(seed=value)
            # Ensure starting location is always open
            if not grid.is_walkable(0, 0):
                raise ValueError("start tile (0,0) must be open")
            self.years[value] = Year(value, grid)
            gen.seed_items(self, value, grid)
            had_start = self.has_monster(value, 0, 0)
            gen.seed_monsters_for_year(self, value, self.global_seed)
            # Ensure starting tile is clear unless a monster was explicitly placed
            if not had_start:
                self.remove_monster(value, 0, 0)
        return self.years[value]
