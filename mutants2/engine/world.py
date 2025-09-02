from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Set, Optional, Iterable

from .senses import Direction
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
    def __init__(self, ground: Optional[Dict[Tuple[int, int, int], str]] = None, seeded_years: Optional[Set[int]] = None):
        self.years: Dict[int, Year] = {}
        self.ground: Dict[Tuple[int, int, int], str] = ground or {}
        self.seeded_years: Set[int] = set(seeded_years or [])

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
        return self.years[value]
