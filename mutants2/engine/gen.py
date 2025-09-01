import random
from typing import Dict, Set, Tuple

from .world import Grid, World
from .items import SPAWNABLE_KEYS

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


def seed_items(world: World, year: int, grid: Grid) -> None:
    """Seed spawnable items on walkable tiles for ``year`` if not already done."""
    if year in world.seeded_years:
        return
    walkable = [(x, y) for x in range(grid.width) for y in range(grid.height) if grid.is_walkable(x, y)]
    rand = random.Random(SEED + year)
    target = round(0.05 * len(walkable))
    if target <= 0:
        world.seeded_years.add(year)
        return
    cells = rand.sample(walkable, min(target, len(walkable)))
    for x, y in cells:
        key = rand.choice(SPAWNABLE_KEYS)
        world.set_ground_item(year, x, y, key)
    world.seeded_years.add(year)
