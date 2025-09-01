from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Set


Direction = str
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
    def __init__(self):
        from . import gen
        grid = gen.generate()
        self.years: Dict[int, Year] = {2000: Year(2000, grid)}

    def year(self, value: int) -> Year:
        return self.years[value]
