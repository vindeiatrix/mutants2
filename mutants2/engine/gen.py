import random
from typing import Dict, Set, Tuple

from .world import Grid

WIDTH = 30
HEIGHT = 30
SEED = 42


def generate(width: int = WIDTH, height: int = HEIGHT, seed: int = SEED) -> Grid:
    rand = random.Random(seed)
    adj: Dict[Tuple[int, int], Set[str]] = {(x, y): set() for x in range(width) for y in range(height)}

    def dirs():
        d = [
            ('north', (0, 1), 'south'),
            ('south', (0, -1), 'north'),
            ('east', (1, 0), 'west'),
            ('west', (-1, 0), 'east'),
        ]
        rand.shuffle(d)
        return d

    visited = set()

    def dfs(x: int, y: int) -> None:
        visited.add((x, y))
        for name, (dx, dy), opp in dirs():
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                adj[(x, y)].add(name)
                adj[(nx, ny)].add(opp)
                dfs(nx, ny)

    dfs(0, 0)

    # Carve a small plaza around (0,0)
    fixed_dirs = [
        ('north', (0, 1), 'south'),
        ('south', (0, -1), 'north'),
        ('east', (1, 0), 'west'),
        ('west', (-1, 0), 'east'),
    ]
    for x in range(3):
        for y in range(3):
            for name, (dx, dy), opp in fixed_dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 3 and 0 <= ny < 3:
                    adj[(x, y)].add(name)
                    adj[(nx, ny)].add(opp)

    return Grid(width, height, adj)
